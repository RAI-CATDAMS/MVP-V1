// server.js

const WebSocket = require('ws');
const fetch = require('node-fetch');
const express = require('express');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

const BACKEND_ENDPOINT = "https://catdams-app-mv-d5fgg9fhc6g5hwg7.eastus-01.azurewebsites.net/ingest";
const wss = new WebSocket.Server({ port: 8080 });

console.log("CATDAMS WebSocket Server running on ws://localhost:8080");

// ----- WEBSOCKET HANDLING -----
wss.on('connection', function connection(ws) {
    console.log('Client connected');

    ws.on('close', function () {
        console.log('Client disconnected');
    });

    ws.on('message', function incoming(message) {
        let msgStr = message;
        if (Buffer.isBuffer(message)) {
            msgStr = message.toString('utf8');
        }
        try {
            const data = JSON.parse(msgStr);
            console.log('Received from client (JSON):', data);

            // POST to Azure backend
            fetch(BACKEND_ENDPOINT, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(response => {
                if (!response.ok) {
                    return response.text().then(txt => {
                        console.error('POST failed with status:', response.status, txt);
                    });
                }
                console.log('POST to backend:', response.status);
            })
            .catch(err => {
                console.error('POST to backend failed:', err);
            });

        } catch (e) {
            console.log('Received from client (Raw):', msgStr);
        }
    });
});

// ====== HTTP POST endpoint to broadcast data to all dashboard clients ======
app.post('/broadcast', (req, res) => {
    try {
        const data = req.body;
        console.log('[BROADCAST] Received at /broadcast:', data);

        // Stringify and send to ALL open WebSocket clients (dashboards)
        const dataStr = JSON.stringify(data);
        wss.clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
                client.send(dataStr);
            }
        });
        res.sendStatus(200);
    } catch (err) {
        console.error('Error in /broadcast:', err);
        res.status(500).send('Failed to broadcast');
    }
});

app.listen(8081, () => {
    console.log('CATDAMS Broadcast HTTP server running on http://localhost:8081');
});
