import requests

url = "https://smartdevicemanagement.googleapis.com/v1/enterprises/ecd8ed99-752a-4001-9554-cd7fe09d4034/devices"
headers = {
    "Authorization": "ya29.a0AcM612x-9sIRwN9pU8l6bZsOIpucXXBQXzYfVziQkdRPBRXkg5K3sfOSBD8FHtwQT31yUiJaAiaNzh2I-9lAemCKZZw9tQwdvyKdQSAsZB7c_vV5dITkv2bKqPUiTjG3-kYhXGR3u_ZmqoU6PaMQdUqtRHVh7HptY8dfiONgaCgYKAeQSARISFQHGX2MiANWIBonn9T6Mr0Qc1QB8og0175",
}

response = requests.get(url, headers=headers)
devices = response.json()
print(devices)
