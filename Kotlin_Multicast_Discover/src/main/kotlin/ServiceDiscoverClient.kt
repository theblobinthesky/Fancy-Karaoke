import java.net.DatagramPacket
import java.net.InetAddress
import java.net.InetSocketAddress
import java.net.NetworkInterface
import java.net.StandardProtocolFamily
import java.net.StandardSocketOptions
import java.nio.ByteBuffer
import java.nio.channels.DatagramChannel
import java.nio.charset.StandardCharsets
import java.util.function.Consumer

class ServiceDiscoverClient(private val multicastIp: InetAddress,
                            private val networkInterface: NetworkInterface,
                            private val serviceId: String, private val port: Int) {

    private val channel: DatagramChannel = DatagramChannel.open(StandardProtocolFamily.INET)
    private var consumer: Consumer<InetAddress> = Consumer { }

    init {
        channel.setOption(StandardSocketOptions.SO_REUSEADDR, true)
        channel.bind(InetSocketAddress(port))
        channel.setOption(StandardSocketOptions.IP_MULTICAST_IF, networkInterface)
    }

    fun startDiscover(microName: String) {
        val key = channel.join(multicastIp, networkInterface)
        val msg = "HELLO FANCY-KARAOKE FROM $microName"
        val msgBytes = msg.toByteArray(Charsets.UTF_8)
        channel.send(ByteBuffer.wrap(msgBytes), InetSocketAddress(multicastIp, port))

        var found = false
        while (!found) {
            val bytebuffer = ByteBuffer.allocate(1024);
            val srcAddress = channel.receive(bytebuffer)
            bytebuffer.flip()
            val bytes = ByteArray(bytebuffer.remaining())
            bytebuffer.get(bytes)

            val recvMsg = String(bytes, StandardCharsets.UTF_8)
            println(recvMsg)
            if ("GREETINGS FROM FANCY-KARAOKE" == recvMsg) {
                found = true;

                if (srcAddress is InetSocketAddress) {
                    consumer.accept(srcAddress.address)
                }
            }
        }
        key.drop()
    }

    fun setOnServiceDiscovered(consumer: Consumer<InetAddress>) {
        this.consumer = consumer
    }

}

fun createNewDiscoverClient(multicastIp: InetAddress, networkInterface: NetworkInterface, serviceId: String, port: Int): ServiceDiscoverClient {
    val discoverClient: ServiceDiscoverClient = ServiceDiscoverClient(multicastIp, networkInterface, serviceId, port)
    return discoverClient
}