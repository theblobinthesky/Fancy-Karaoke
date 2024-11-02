import java.net.InetAddress
import java.net.NetworkInterface
import java.util.stream.Collectors

fun main(args: Array<String>) {
    val possibleIntf = NetworkInterface.networkInterfaces().filter { intf ->
        intf.isUp && intf.supportsMulticast()
    }.collect(Collectors.toList())

    if (possibleIntf.isNotEmpty()) {
        val discoverClient: ServiceDiscoverClient = createNewDiscoverClient(
            InetAddress.getByName("239.255.255.250"), possibleIntf[0], "fancy_caraoke", 4003)
        discoverClient.setOnServiceDiscovered { addr ->
            println(addr.hostAddress)
        }
        discoverClient.startDiscover()
    } else {
        println("No interface found");
    }


}