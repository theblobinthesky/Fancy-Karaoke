using System.Collections;
using System.Collections.Concurrent;
using System.Net;
using System.Net.Sockets;

namespace Server_Console;

// https://www.codeplanet.eu/tutorials/csharp/4-tcp-ip-socket-programmierung-in-csharpf0e5.html?start=3
public class MulticastNetwork
{
    private readonly Socket _socket;
    private readonly IPAddress _multicastAddress;
    private readonly IPEndPoint _multicastEndpoint;
    private readonly IPEndPoint _recievePoint;

    public MulticastNetwork(IPAddress multicastAddress, int multicastPort)
    {
        _multicastAddress = multicastAddress;
        _multicastEndpoint = new IPEndPoint(multicastAddress, multicastPort);

        _socket = new Socket(AddressFamily.InterNetwork, SocketType.Dgram, ProtocolType.Udp);

        try
        {
            _socket.Bind(new IPEndPoint(IPAddress.Any, multicastPort));
            _socket.SetSocketOption(SocketOptionLevel.IP, SocketOptionName.AddMembership,
                new MulticastOption(multicastAddress, IPAddress.Any));
        }
        catch (SocketException e)
        {
            Console.WriteLine(e.ToString());
            _socket.Close();
        }

        _recievePoint = new IPEndPoint(IPAddress.Any, 0);
    }

    public (EndPoint, byte[], int) Receive()
    {
        byte[] buffer = new byte[1024];
        EndPoint peerEndpoint = new IPEndPoint(IPAddress.Any, 0);
        int length = _socket.ReceiveFrom(buffer, 0, 1024, SocketFlags.None, ref peerEndpoint);
        return (peerEndpoint, buffer, length);
    }

    public void Send(byte[] data)
    {
        _socket.SendTo(data, 0, data.Length, SocketFlags.None, _multicastEndpoint);
    }

    public void Close()
    {
        _socket.SetSocketOption(SocketOptionLevel.IP, SocketOptionName.DropMembership,
            new MulticastOption(_multicastAddress, IPAddress.Any));
        _socket.Close();
    }
}

public record TcpAccept(Socket Socket);

public record TcpResult(Socket Socket, byte[] Data, int DataLength);

// 
public class TcpNetwork
{
    private readonly Socket _listenerSocket;
    private readonly List<Socket> _clientSockets;

    public TcpNetwork(IPAddress localAddress, int localPort)
    {
        _listenerSocket = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp);
        _listenerSocket.Bind(new IPEndPoint(localAddress, localPort));
        _listenerSocket.Listen();
        _clientSockets = new List<Socket>();
    }

    public (List<TcpAccept>, List<TcpResult>) Select()
    {
        List<Socket> allSockets = new List<Socket>();
        allSockets.Add(_listenerSocket);
        allSockets.AddRange(_clientSockets);

        Socket.Select(allSockets, null, null, -1);

        List<TcpAccept> accepts = new List<TcpAccept>();
        List<TcpResult> results = new List<TcpResult>();
        foreach (Socket socket in allSockets)
        {
            if (socket == _listenerSocket)
            {
                Socket clientSocket = socket.Accept();
                _clientSockets.Add(clientSocket);
                accepts.Add(new TcpAccept(clientSocket));
            }
            else
            {
                byte[] buffer = new byte[1024];
                int bytesReceived = socket.Receive(buffer); // TODO: Guard for buffer overflow.

                if (bytesReceived > 0)
                {
                    results.Add(new TcpResult(socket, buffer, bytesReceived));
                }
                else
                {
                    socket.Close();
                    _clientSockets.Remove(socket);
                }
            }
        }

        return (accepts, results);
    }

    public void Close()
    {
        _listenerSocket.Close();
        foreach (Socket socket in _clientSockets)
        {
            socket.Close();
        }
    }

    public void CloseClient(Socket socket)
    {
        _clientSockets.Remove(socket);
        socket.Shutdown(SocketShutdown.Both);
        socket.Close();
    }
}

class NetworkState
{
    public bool IsAccepted { get; set; }
}

class NetworkManager
{
    private readonly ConcurrentQueue<(IPEndPoint, string)> _queuedDevices;
    private readonly MulticastNetwork _multicastNetwork;
    private readonly TcpNetwork _tcpNetwork;

    private bool _listening;
    private readonly Thread _multicastThread;
    private readonly Thread _tcpThread;

    private readonly Dictionary<Socket, NetworkState> _deviceStates;

    public NetworkManager(MulticastNetwork multicastNetwork, TcpNetwork tcpNetwork)
    {
        _queuedDevices = new ConcurrentQueue<(IPEndPoint, string)>();
        _multicastNetwork = multicastNetwork;
        _tcpNetwork = tcpNetwork;
        _multicastThread = new Thread(start: StartMulticast);
        _tcpThread = new Thread(start: StartTcpAcceptor);
        _deviceStates = new Dictionary<Socket, NetworkState>();
    }

    public void Listen()
    {
        _listening = true;
        _multicastThread.Start();
        _tcpThread.Start();
    }

    private void StartMulticast()
    {
        var utf8 = System.Text.Encoding.UTF8;

        while (_listening)
        {
            (EndPoint, byte[], int) buffer = _multicastNetwork.Receive();
            String request = utf8.GetString(buffer.Item2, 0, buffer.Item3);

            String preamble = "HELLO FANCY-KARAOKE FROM ";
            if (request.StartsWith(preamble))
            {
                String micName = request.Remove(preamble.Length);
                _queuedDevices.Enqueue(((IPEndPoint)buffer.Item1, micName));
                _multicastNetwork.Send(utf8.GetBytes("GREETINGS FROM FANCY-KARAOKE"));
            }
        }
    }

    private void StartTcpAcceptor()
    {
        var utf8 = System.Text.Encoding.UTF8;

        while (_listening)
        {
            (List<TcpAccept>, List<TcpResult>) results = _tcpNetwork.Select();
            foreach (TcpAccept accept in results.Item1)
            {
                accept.Socket.Send(utf8.GetBytes("GREETINGS FROM FANCY-KARAOKE"));
            }

            foreach (TcpResult result in results.Item2)
            {
                if (!_deviceStates.ContainsKey(result.Socket))
                {
                    _deviceStates.Add(result.Socket, new NetworkState());
                }

                NetworkState state = _deviceStates[result.Socket];
                if (state.IsAccepted)
                {
                    Console.WriteLine("Got bytes: " + result.DataLength);
                }
                else
                {
                    Console.Write(result.Socket.RemoteEndPoint?.ToString());
                    Console.Write(" [request accept] ");
                    Console.Write(": ");
                    Console.WriteLine(utf8.GetString(result.Data, 0, result.DataLength));

                    if (true)
                    {
                        result.Socket.Send(utf8.GetBytes("ACCEPTED"));
                    }
                    else
                    {
                        Console.Write(result.Socket.RemoteEndPoint?.ToString());
                        Console.Write(" [denied]");
                        
                        result.Socket.Send(utf8.GetBytes("DENIED"));
                        _tcpNetwork.CloseClient(result.Socket);
                        _deviceStates.Remove(result.Socket);
                    }

                    state.IsAccepted = true;
                }
            }
        }
    }

    public void Join()
    {
        _multicastThread.Join();
        _tcpThread.Join();
    }


    public void Close()
    {
        _multicastNetwork.Close();
        _tcpNetwork.Close();
        _listening = false;
    }
}