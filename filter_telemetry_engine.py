import time
from collections import deque

class FiltrationState:
    NORMAL = "NORMAL_OPERATION"
    WARNING = "WARNING_THRESHOLD_REACHED"
    BYPASS_ENGAGED = "EMERGENCY_BYPASS_ACTIVE"
    FAULT = "SYSTEM_FAULT_LOCKOUT"

class SystemTelemetryEngine:
    def __init__(self, buffer_size=10, pressure_limit_bar=4.5):
        self.buffer_size = buffer_size
        self.pressure_limit = pressure_limit_bar
        self.pressure_log = deque(maxlen=buffer_size)
        self.current_state = FiltrationState.NORMAL
        self.bypass_valve_open = False
        self.cycle_count = 0

    def ingest_sensor_reading(self, raw_voltage: float, flow_rate: float):
        calculated_pressure = round(max(0.0, (raw_voltage * 1.25) - 0.2), 2)
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        self.pressure_log.append(calculated_pressure)
        self.cycle_count += 1

        self._evaluate_state_machine(calculated_pressure, flow_rate)
        
        return {
            "time": timestamp,
            "cycle": self.cycle_count,
            "pressure": calculated_pressure,
            "state": self.current_state,
            "bypass": self.bypass_valve_open
        }

    def _evaluate_state_machine(self, current_pressure: float, flow_rate: float):
        avg_pressure = sum(self.pressure_log) / len(self.pressure_log)

        if current_pressure >= self.pressure_limit:
            self.current_state = FiltrationState.BYPASS_ENGAGED
            self.bypass_valve_open = True
        elif avg_pressure >= (self.pressure_limit * 0.8):
            self.current_state = FiltrationState.WARNING
            self.bypass_valve_open = False
        elif flow_rate <= 0.1 and current_pressure > 3.0:
            self.current_state = FiltrationState.FAULT
            self.bypass_valve_open = True
        else:
            self.current_state = FiltrationState.NORMAL
            self.bypass_valve_open = False

if __name__ == "__main__":
    engine = SystemTelemetryEngine(buffer_size=5, pressure_limit_bar=4.0)
    
    mock_sensor_stream = [
        (1.5, 2.2), (1.8, 2.1), (2.4, 1.9), 
        (3.1, 1.5), (3.6, 1.0), (4.2, 0.4)
    ]

    print("--- Low-Level Telemetry & State Machine Execution Log ---")
    for voltage, flow in mock_sensor_stream:
        status = engine.ingest_sensor_reading(voltage, flow)
        print(f"[{status['time']} | Cycle {status['cycle']}]: Basınç: {status['pressure']} bar | Durum: {status['state']} | Vana: {'AÇIK' if status['bypass'] else 'KAPALI'}")