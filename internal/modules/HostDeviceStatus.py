import psutil
import subprocess

class HostDeviceStatus:

    def getCPUTemperature(self) -> str:
        try:
            temperature = psutil.sensors_temperatures()
            cpu_temperature = temperature['coretemp'][0].current  # Gantilah 'coretemp' dengan sensor yang sesuai pada sistem Anda
            return f"{cpu_temperature}°C"
        except Exception as e:
            return f"{e}"
    
    def getCPUUsage(self) -> str:
        cpu_percent = psutil.cpu_percent(interval=1)
        return f"{cpu_percent}%"
    
    def getMemoryUsage(self) -> str:
        memory = psutil.virtual_memory()
        return f"{memory.used / (1024 ** 3):.2f} GB"
    
    def getMemoryFree(self) -> str:
        memory = psutil.virtual_memory()
        return f"{memory.available / (1024 ** 3):.2f} GB"
    
    def getMemoryTotal(self) -> str:
        memory = psutil.virtual_memory()
        return f"{memory.total / (1024 ** 3):.2f} GB"

    def getStorageInfo(self) -> dict[str, str]:
        disk_partitions = psutil.disk_partitions()
        usage = psutil.disk_usage(disk_partitions[0].mountpoint)
        return {
            "partition": f"{disk_partitions[0].device}",
            "total_space": f"{usage.total / (1024 ** 3):.2f} GB",
            "used_space": f"{usage.used / (1024 ** 3):.2f} GB",
            "free_space": f"{usage.free / (1024 ** 3):.2f} GB",
            "disk_usage": f"{usage.percent}%"
        }
        
    def getUpTime(self) -> str:
        uptime = psutil.boot_time()
        return f"{uptime} seconds"
    
    def getFanSpeed(self) -> str:
        output = subprocess.check_output(["sensors"]).decode("utf-8")
        fan_speed_lines = [line for line in output.split('\n') if 'fan' in line.lower()]
        return fan_speed_lines[0]
    
    def brief(self):
        return {
            "cpu_temp": self.getCPUTemperature(),
            "cpu_usage": self.getCPUUsage(),
            "memory_usage": self.getMemoryUsage(),
            "memory_free": self.getMemoryFree(),
            "memory_total": self.getMemoryTotal(),
            "storage": self.getStorageInfo(),
            "up_time": self.getUpTime(),
            "fan_speed": self.getFanSpeed(),
        }