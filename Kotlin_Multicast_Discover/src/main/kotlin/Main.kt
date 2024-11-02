import java.net.Inet4Address
import java.net.InetAddress
import java.net.InetSocketAddress
import java.net.NetworkInterface
import java.net.Socket
import java.nio.charset.StandardCharsets
import java.util.Random
import java.util.stream.Collectors

fun main(args: Array<String>) {
    val possibleIntf = NetworkInterface.networkInterfaces().filter { intf ->
        intf.isUp && intf.inetAddresses.toList().any { addr -> addr is Inet4Address } && intf.supportsMulticast()
    }.collect(Collectors.toList())

    if (possibleIntf.isNotEmpty()) {
        val discoverClient: ServiceDiscoverClient = createNewDiscoverClient(
            InetAddress.getByName("239.255.255.250"), possibleIntf[0], "fancy_caraoke", 4003)
        discoverClient.setOnServiceDiscovered { addr ->
            println(addr.hostAddress)

            val socket = Socket()
            socket.connect(InetSocketAddress(addr, 4004))
            val bytes = ByteArray(1024)
            val read = socket.getInputStream().read(bytes)
            val msg = String(bytes.copyOf(read), StandardCharsets.UTF_8)

            println(msg)

            if ("GREETINGS FROM FANCY-KARAOKE" == msg) {
                val random = Random().nextInt(1000, 10000)
                socket.getOutputStream().write(random.toString(10).toByteArray(StandardCharsets.UTF_8))
                socket.getOutputStream().flush()

                val bytesStatus = ByteArray(1024)
                val readStatus = socket.getInputStream().read(bytesStatus)
                val msgStatus = String(bytesStatus.copyOf(readStatus), StandardCharsets.UTF_8)

                println(msgStatus)
                if (msgStatus == "ACCEPTED") {
                    val random = Random()
                    for (i in 0..5)  {
                        val bytesData = ByteArray(1024)
                        random.nextBytes(bytesData)
                        socket.getOutputStream().write(bytesData)
                        socket.getOutputStream().flush()
                    }
                    socket.close()
                } else {
                    socket.close()
                }
            }
        }
        discoverClient.startDiscover("test-mic")
    } else {
        println("No interface found");
    }


}