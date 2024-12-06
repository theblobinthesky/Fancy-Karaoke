package com.example.caraoke_app

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.dp
import androidx.core.app.ActivityCompat
import com.example.caraoke_app.model.Audio
import com.example.caraoke_app.model.connectToServer
import com.example.caraoke_app.model.createServiceDiscover
import com.example.caraoke_app.ui.theme.CaraokeAppTheme
import kotlinx.coroutines.launch
import java.net.InetAddress

data class Server(val address: InetAddress)

class MainActivity : ComponentActivity() {
    private var _servers = mutableStateListOf<Server>()
    val servers: List<Server> get() = _servers

    val audio: Audio = Audio()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            CaraokeAppTheme {
                Surface(color = MaterialTheme.colorScheme.background) {
                    ServerConnectApp()
                }
            }
        }

        createServiceDiscover("test-mic") { address: InetAddress ->
            val server = Server(address)
            if (!_servers.contains(server)) {
                _servers.add(Server(address))
            }
        }
    }

    @OptIn(ExperimentalMaterial3Api::class)
    @Composable
    fun ServerConnectApp() {
        var connectedServer by remember { mutableStateOf<Server?>(null) }
        var isTransmitting by remember { mutableStateOf(false) }
        var isSearching by remember { mutableStateOf(true) }
        val snackbarHostState = remember { SnackbarHostState() }
        val coroutineScope = rememberCoroutineScope()

        // Permission Handling
        val context = LocalContext.current
        var hasAudioPermission by remember {
            mutableStateOf(
                ActivityCompat.checkSelfPermission(
                    context, Manifest.permission.RECORD_AUDIO
                ) == PackageManager.PERMISSION_GRANTED
            )
        }

        val permissionLauncher = rememberLauncherForActivityResult(
            ActivityResultContracts.RequestPermission()
        ) { isGranted ->
            hasAudioPermission = isGranted
            if (!isGranted) {
                coroutineScope.launch {
                    snackbarHostState.showSnackbar("Audio permission is required to transmit.")
                }
            }
        }

        LaunchedEffect(Unit) {
            if (!hasAudioPermission) {
                permissionLauncher.launch(Manifest.permission.RECORD_AUDIO)
            }
        }

        Scaffold(snackbarHost = { SnackbarHost(hostState = snackbarHostState) }, topBar = {
            TopAppBar(title = { Text("Caraoke Connect") })
        }) { paddingValues ->
            Box(
                modifier = Modifier
                    .padding(paddingValues)
                    .fillMaxSize()
            ) {
                when {
                    connectedServer == null -> {
                        // Display list of servers with loading indicator below
                        Column(
                            modifier = Modifier.fillMaxSize()
                        ) {
                            ServerList(servers = servers, onServerSelected = { server ->
                                if (hasAudioPermission) {
                                    connectedServer = server
                                    isTransmitting = false
                                    audio.initAudio()
                                    audio.setOnCancel({ -> isTransmitting = false; connectedServer = null })
                                    connectToServer(server.address, audio)
                                } else {
                                    coroutineScope.launch {
                                        snackbarHostState.showSnackbar("Audio permission not granted.")
                                    }
                                }
                            })
                            // Loading indicator below the list
                            if (isSearching) {
                                Row(
                                    modifier = Modifier
                                        .fillMaxWidth()
                                        .padding(16.dp),
                                    verticalAlignment = Alignment.CenterVertically,
                                    horizontalArrangement = Arrangement.Center
                                ) {
                                    CircularProgressIndicator()
                                    Spacer(modifier = Modifier.width(8.dp))
                                    Text("Searching for servers...")
                                }
                            }
                        }
                    }

                    else -> {
                        // Connecting or Connected
                        ConnectionScreen(server = connectedServer!!,
                            isTransmitting = isTransmitting,
                            onConnect = {
                                // TODO: Connect.
                                isTransmitting = true
                            },
                            onStop = {
                                // TODO: Stop.
                                isTransmitting = false
                                connectedServer = null
                                audio.stopRecord()
                            })
                    }
                }
            }
        }
    }
}

@Composable
fun ServerList(servers: List<Server>, onServerSelected: (Server) -> Unit) {
    LazyColumn(
        modifier = Modifier
            .fillMaxWidth()
            .padding(16.dp)
    ) {
        items(servers) { server ->
            ServerItem(server = server, onClick = { onServerSelected(server) })
            HorizontalDivider()
        }
    }
}

@Composable
fun ServerItem(server: Server, onClick: () -> Unit) {
    Row(modifier = Modifier
        .fillMaxWidth()
        .clickable { onClick() }
        .padding(vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically) {
        Text(text = server.address.toString(), style = MaterialTheme.typography.bodyMedium)
    }
}

@Composable
fun ConnectionScreen(
    server: Server, isTransmitting: Boolean, onConnect: () -> Unit, onStop: () -> Unit
) {
    LaunchedEffect(server, isTransmitting) {
        if (!isTransmitting) {
            onConnect()
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "Connected to ${server.address.toString()}",
            style = MaterialTheme.typography.headlineMedium
        )
        Spacer(modifier = Modifier.height(24.dp))
        if (isTransmitting) {
            AnimatedMicIndicator()
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = "Listening to microphone...", style = MaterialTheme.typography.bodyLarge
            )
            Spacer(modifier = Modifier.height(24.dp))
            Button(onClick = onStop) {
                Text("Stop Transmitting")
            }
        } else {
            CircularProgressIndicator()
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = "Connecting...", style = MaterialTheme.typography.bodyLarge
            )
        }
    }
}

@Composable
fun AnimatedMicIndicator() {
    // Multiple pulsing circles for a more appealing animation
    val infiniteTransition = rememberInfiniteTransition()
    val pulse1 by infiniteTransition.animateFloat(
        initialValue = 45f, targetValue = 55f, animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = FastOutSlowInEasing), repeatMode = RepeatMode.Reverse
        ), label = "pulse1"
    )
    val pulse2 by infiniteTransition.animateFloat(
        initialValue = 50f, targetValue = 55f, animationSpec = infiniteRepeatable(
            animation = tween(1200, easing = FastOutSlowInEasing), repeatMode = RepeatMode.Reverse
        ), label = "pulse2"
    )
    val pulse3 by infiniteTransition.animateFloat(
        initialValue = 40f, targetValue = 55f, animationSpec = infiniteRepeatable(
            animation = tween(1400, easing = FastOutSlowInEasing), repeatMode = RepeatMode.Reverse
        ), label = "pulse3"
    )

    Box(
        contentAlignment = Alignment.Center, modifier = Modifier.size(120.dp)
    ) {
        Canvas(modifier = Modifier.size(120.dp)) {
            drawCircle(
                color = Color.Red.copy(alpha = 0.5f),
                radius = pulse1,
                center = Offset(size.width / 2, size.height / 2)
            )
            drawCircle(
                color = Color.Red.copy(alpha = 0.3f),
                radius = pulse2,
                center = Offset(size.width / 2, size.height / 2)
            )
            drawCircle(
                color = Color.Red.copy(alpha = 0.1f),
                radius = pulse3,
                center = Offset(size.width / 2, size.height / 2)
            )
        }
        Image(
            painterResource(id = R.drawable.ic_mic),
            contentDescription = "Microphone",
            modifier = Modifier.size(50.dp)
        )
    }
}