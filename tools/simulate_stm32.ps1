# ==============================================================================
# simulate_stm32.ps1 - Simulates STM32L475 telemetry publishing to MQTT
# ==============================================================================
param (
    [string] = "localhost",
    [int] = 1883,
    [int] = 60,
    [int] = 1
)

Write-Host "Starting STM32L475 MQTT Telemetry Simulation ( cycles)..." -ForegroundColor Cyan
Write-Host "Target Broker: :" -ForegroundColor DarkCyan

 = "C:\Program Files\mosquitto\mosquitto_pub.exe"
 = Test-Path 

for ( = 1;  -le ; ++) {
    # Generate realistic telemetry around nominal values
     = [math]::Round(25.5 + (Get-Random -Minimum -20 -Maximum 20) / 10.0, 2)
      = [math]::Round(58.0 + (Get-Random -Minimum -40 -Maximum 40) / 10.0, 2)
     = [math]::Round(1013.2 + (Get-Random -Minimum -10 -Maximum 10) / 10.0, 1)

    if () {
        &  -h  -p  -t "/temperature" -m ""
        &  -h  -p  -t "/humidite" -m ""
        &  -h  -p  -t "/pression" -m ""
    } else {
        # Fallback to python one-liner if mosquitto_pub is not in standard path
        python -c "import paho.mqtt.publish as p; p.single('/temperature', '', hostname='', port=); p.single('/humidite', '', hostname='', port=); p.single('/pression', '', hostname='', port=)"
    }

    Write-Host "[/] Telemetry sent -> T:  C | H:  % | P:  hPa" -ForegroundColor Green
    Start-Sleep -Seconds 
}

Write-Host "Simulation completed!" -ForegroundColor Cyan
