// MainActivity.kt
package com.example.caraoke_app

import android.Manifest
import android.content.pm.PackageManager
import android.graphics.drawable.Drawable
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
import com.example.caraoke_app.ui.theme.CaraokeAppTheme
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

data class Server(val name: String, val address: String)

class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            CaraokeAppTheme {
                Surface(color = MaterialTheme.colorScheme.background) {
                    ServerConnectApp()
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ServerConnectApp() {
    var connectedServer by remember { mutableStateOf<Server?>(null) }
    var isTransmitting by remember { mutableStateOf(false) }
    var isSearching by remember { mutableStateOf(true) }
    var servers by remember { mutableStateOf<List<Server>>(emptyList()) }
    val snackbarHostState = remember { SnackbarHostState() }
    val coroutineScope = rememberCoroutineScope()

    // Permission Handling
    val context = LocalContext.current
    var hasAudioPermission by remember {
        mutableStateOf(
            ActivityCompat.checkSelfPermission(
                context,
                Manifest.permission.RECORD_AUDIO
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

    // Continuous server search simulation
    LaunchedEffect(Unit) {
        while (isActive) {
            if (isSearching) {
                delay(2000) // Simulate network search delay
                // Simulate adding a new server
                val newServerNumber = servers.size + 1
                val newServer = Server("Server $newServerNumber", "192.168.1.${1 + newServerNumber}")
                servers = servers + newServer
                coroutineScope.launch {
                    snackbarHostState.showSnackbar("Discovered ${newServer.name}")
                }
            }
            delay(5000) // Repeat every 5 seconds
        }
    }

    Scaffold(
        snackbarHost = { SnackbarHost(hostState = snackbarHostState) },
        topBar = {
            SmallTopAppBar(title = { Text("Caraoke Connect") })
        }
    ) { paddingValues ->
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
                                coroutineScope.launch {
                                    snackbarHostState.showSnackbar("Connecting to ${server.name}...")
                                }
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
                    ConnectionScreen(
                        server = connectedServer!!,
                        isTransmitting = isTransmitting,
                        onConnect = {
                            coroutineScope.launch {
                                delay(1000) // Simulate connection delay
                                isTransmitting = true
                                snackbarHostState.showSnackbar("Connected to ${connectedServer!!.name}")
                            }
                        },
                        onStop = {
                            isTransmitting = false
                            connectedServer = null
                            coroutineScope.launch {
                                snackbarHostState.showSnackbar("Disconnected.")
                            }
                        }
                    )
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
            Divider()
        }
    }
}

@Composable
fun ServerItem(server: Server, onClick: () -> Unit) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .clickable { onClick() }
            .padding(vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(text = server.name, style = MaterialTheme.typography.titleMedium)
        Spacer(modifier = Modifier.weight(1f))
        Text(text = server.address, style = MaterialTheme.typography.bodyMedium)
    }
}

@Composable
fun ConnectionScreen(
    server: Server,
    isTransmitting: Boolean,
    onConnect: () -> Unit,
    onStop: () -> Unit
) {
    val coroutineScope = rememberCoroutineScope()

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
            text = "Connected to ${server.name}",
            style = MaterialTheme.typography.headlineMedium
        )
        Spacer(modifier = Modifier.height(24.dp))
        if (isTransmitting) {
            AnimatedMicIndicator()
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = "Listening to microphone...",
                style = MaterialTheme.typography.bodyLarge
            )
            Spacer(modifier = Modifier.height(24.dp))
            Button(onClick = onStop) {
                Text("Stop Transmitting")
            }
        } else {
            CircularProgressIndicator()
            Spacer(modifier = Modifier.height(16.dp))
            Text(
                text = "Connecting...",
                style = MaterialTheme.typography.bodyLarge
            )
        }
    }
}

@Composable
fun AnimatedMicIndicator() {
    // Multiple pulsing circles for a more appealing animation
    val infiniteTransition = rememberInfiniteTransition()
    val pulse1 by infiniteTransition.animateFloat(
        initialValue = 20f,
        targetValue = 40f,
        animationSpec = infiniteRepeatable(
            animation = tween(1000, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        )
    )
    val pulse2 by infiniteTransition.animateFloat(
        initialValue = 15f,
        targetValue = 35f,
        animationSpec = infiniteRepeatable(
            animation = tween(1200, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        )
    )
    val pulse3 by infiniteTransition.animateFloat(
        initialValue = 10f,
        targetValue = 30f,
        animationSpec = infiniteRepeatable(
            animation = tween(1400, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Reverse
        )
    )

    Box(
        contentAlignment = Alignment.Center,
        modifier = Modifier.size(100.dp)
    ) {
        Canvas(modifier = Modifier.size(100.dp)) {
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
            modifier = Modifier.size(40.dp)
        )
    }
}