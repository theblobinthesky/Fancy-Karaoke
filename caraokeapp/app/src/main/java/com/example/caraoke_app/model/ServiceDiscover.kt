package com.example.caraoke_app.model

import java.net.Inet4Address
import java.net.InetAddress
import java.net.InetSocketAddress
import java.net.NetworkInterface
import java.net.Socket
import java.net.StandardProtocolFamily
import java.net.StandardSocketOptions
import java.nio.ByteBuffer
import java.nio.channels.DatagramChannel
import java.nio.channels.SelectionKey
import java.nio.channels.Selector
import java.nio.charset.StandardCharsets
import java.util.concurrent.Executors
import java.util.function.Consumer
import java.util.stream.Collectors
import kotlin.random.Random

class ServiceDiscover(
    private val multicastIp: InetAddress,
    private val networkInterface: NetworkInterface,
    private val serviceId: String, private val port: Int
) {
    private val channel: DatagramChannel = DatagramChannel.open(StandardProtocolFamily.INET)
    private var consumer: Consumer<InetAddress> = Consumer { }
    private var onSearch: Boolean = false

    init {
        channel.setOption(StandardSocketOptions.SO_REUSEADDR, true)
        channel.bind(InetSocketAddress("0.0.0.0", port))
        channel.configureBlocking(false)
        channel.setOption(StandardSocketOptions.IP_MULTICAST_IF, networkInterface)
    }

    fun startDiscover(microName: String) {
        val key = channel.join(multicastIp, networkInterface)
        val msg = "HELLO FANCY-KARAOKE FROM $microName"
        val msgBytes = msg.toByteArray(Charsets.UTF_8)
        onSearch = true

        val selector = Selector.open()
        val selectorKey = channel.register(selector, SelectionKey.OP_READ)

        val msgRecieved = Consumer<SelectionKey> { selKey ->
            if (selKey.channel() is DatagramChannel) {
                val bytebuffer = ByteBuffer.allocate(1024);
                val srcAddress = (selKey.channel() as DatagramChannel).receive(bytebuffer)
                bytebuffer.flip()
                val bytes = ByteArray(bytebuffer.remaining())
                bytebuffer.get(bytes)

                val recvMsg = String(bytes, StandardCharsets.UTF_8)
                println(recvMsg)
                if ("GREETINGS FROM FANCY-KARAOKE" == recvMsg) {
                    if (srcAddress is InetSocketAddress) {
                        consumer.accept(srcAddress.address)
                    }
                }
            }
        }

        while (onSearch) {
            channel.send(ByteBuffer.wrap(msgBytes), InetSocketAddress(multicastIp, port))
            selector.select(5000)
            selector.selectedKeys().forEach(msgRecieved)
            Thread.sleep(5000)
        }

        selectorKey.cancel()
        key.drop()
    }

    fun stopDiscover() {
        onSearch = false
    }

    fun setOnServiceDiscovered(consumer: Consumer<InetAddress>) {
        this.consumer = consumer
    }

}

fun createServiceDiscover(name: String, consumer: Consumer<InetAddress>) {
    val possibleIntf = NetworkInterface.getNetworkInterfaces().toList().stream().filter { i ->
        i.isUp && i.inetAddresses.toList()
            .any { addr -> addr is Inet4Address } && i.supportsMulticast()
    }.collect(Collectors.toList())

    if (possibleIntf.isNotEmpty()) {
        val discoverClient = ServiceDiscover(
            InetAddress.getByName("239.255.255.250"), possibleIntf[0], "fancy_caraoke", 4003
        )
        discoverClient.setOnServiceDiscovered(consumer)

        val executor = Executors.newFixedThreadPool(1)
        executor.execute {
            discoverClient.startDiscover(name)
        }
    } else {
        throw RuntimeException("No network interface found.");
    }
}

fun connectToServer(addr: InetAddress, audio: Audio) {
    val service = Executors.newFixedThreadPool(1)
    service.execute {
        val socket = Socket()
        socket.connect(InetSocketAddress(addr, 4004))
        val bytes = ByteArray(1024)
        val read = socket.getInputStream().read(bytes)
        val msg = String(bytes.copyOf(read), StandardCharsets.UTF_8)

        if ("GREETINGS FROM FANCY-KARAOKE" == msg) {
            val random = Random.nextInt(1000, 10000)
            socket.getOutputStream()
                .write(random.toString(10).toByteArray(StandardCharsets.UTF_8))
            socket.getOutputStream().flush()

            val bytesStatus = ByteArray(1024)
            val readStatus = socket.getInputStream().read(bytesStatus)
            val msgStatus = String(bytesStatus.copyOf(readStatus), StandardCharsets.UTF_8)

            println(msgStatus)
            if (msgStatus == "ACCEPTED") {
                audio.record(socket)
            } else {
                socket.close()
            }
        }
    }
}