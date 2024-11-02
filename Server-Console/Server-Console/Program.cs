using System.Net;
using Server_Console;

MulticastNetwork multicastNetwork = new MulticastNetwork(IPAddress.Parse("239.255.255.250"), 4003);
TcpNetwork tcpNetwork = new TcpNetwork(IPAddress.Any, 4004);

NetworkManager manager = new NetworkManager(multicastNetwork, tcpNetwork);
manager.Listen();
manager.Join();
manager.Close();