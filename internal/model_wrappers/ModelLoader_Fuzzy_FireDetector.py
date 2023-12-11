from internal.contracts.ISensorModel import ISensorModel
from typing import Callable, Any
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from internal.helper.helper import getTimeNow


class ModelLoader_Fuzzy_FireDetector(ISensorModel):

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def getModelType() -> str:
        return "dataAnalytic"

    def getModelVersion(self) -> str:
        return "fuzzy_fireDetector@v1.0.0"

    @staticmethod
    def getModelMetadata() -> dict[str, Any]:
        return {
            "model_name": "bme680_fuzzy_fireDetector",
            "version": "v1.0.0",
            "smcb_wrapper_version": "v1.0.0",
        }

    def inferData(self, data: Any, onInfered: Callable[[Any], None], onThresholdExceeded: Callable[[Any], None]):

        temperatureData = data["data_measured"][0]["data"]
        humidityData = data["data_measured"][1]["data"]
        gasData = data["data_measured"][2]["data"]

        dataMeasured = [
            {
                "sensor_type": data["data_measured"][0]["sensor_type"],
                "data":  data["data_measured"][0]["data"],
                "unit_measure":  data["data_measured"][0]["unit_measure"]
            },
            {
                "sensor_type": data["data_measured"][1]["sensor_type"],
                "data":  data["data_measured"][1]["data"],
                "unit_measure":  data["data_measured"][1]["unit_measure"]
            },
            {
                "sensor_type": data["data_measured"][2]["sensor_type"],
                "data":  data["data_measured"][2]["data"],
                "unit_measure":  data["data_measured"][2]["unit_measure"]
            }
        ]

        fire_likelihood_result = self.fuzzy_fire_detector(temperatureData, humidityData, gasData)

        # Define semantic interpretations
        if fire_likelihood_result <= 40:
            onInfered(
                {
                    "dataMeasured": dataMeasured,
                    "inferenceLabelStatus": "low risk",
                    "capturedAt": getTimeNow(format='%Y-%m-%d')
                }
            )
        elif fire_likelihood_result <= 70:
            onInfered(
                {
                    "dataMeasured": dataMeasured,
                    "inferenceLabelStatus": "medium risk",
                    "capturedAt": getTimeNow(format='%Y-%m-%d')
                }
            )
        else:
            onInfered(
                {
                    "dataMeasured": dataMeasured,
                    "inferenceLabelStatus": "high risk",
                    "capturedAt": getTimeNow(format='%Y-%m-%d')
                }
            )
            onThresholdExceeded("danger")

    def fuzzy_fire_detector(self, temperature, humidity, gas_resistance):
        # Define fuzzy variables
        temperature_var = ctrl.Antecedent(np.arange(0, 50, 1), 'temperature')
        humidity_var = ctrl.Antecedent(np.arange(0, 100, 1), 'humidity')
        gas_resistance_var = ctrl.Antecedent(
            np.arange(0, 100000, 1), 'gas_resistance')
        fire_likelihood = ctrl.Consequent(
            np.arange(0, 101, 1), 'fire_likelihood')

        # Define membership functions
        temperature_var['low'] = fuzz.trimf(
            temperature_var.universe, [0, 10, 20])
        temperature_var['medium'] = fuzz.trimf(
            temperature_var.universe, [15, 25, 35])
        temperature_var['high'] = fuzz.trimf(
            temperature_var.universe, [30, 40, 50])

        humidity_var['low'] = fuzz.trimf(humidity_var.universe, [0, 20, 40])
        humidity_var['medium'] = fuzz.trimf(
            humidity_var.universe, [30, 50, 70])
        humidity_var['high'] = fuzz.trimf(humidity_var.universe, [60, 80, 100])

        gas_resistance_var['low'] = fuzz.trimf(
            gas_resistance_var.universe, [0, 20000, 40000])
        gas_resistance_var['medium'] = fuzz.trimf(
            gas_resistance_var.universe, [30000, 50000, 70000])
        gas_resistance_var['high'] = fuzz.trimf(
            gas_resistance_var.universe, [60000, 80000, 100000])

        fire_likelihood['low'] = fuzz.trimf(
            fire_likelihood.universe, [0, 20, 40])
        fire_likelihood['medium'] = fuzz.trimf(
            fire_likelihood.universe, [30, 60, 90])
        fire_likelihood['high'] = fuzz.trimf(
            fire_likelihood.universe, [80, 100, 100])

        # Define fuzzy rules
        rule1 = ctrl.Rule(temperature_var['low'] | humidity_var['low']
                          | gas_resistance_var['low'], fire_likelihood['low'])
        rule2 = ctrl.Rule(temperature_var['medium'] | humidity_var['medium']
                          | gas_resistance_var['medium'], fire_likelihood['medium'])
        rule3 = ctrl.Rule(temperature_var['high'] | humidity_var['high']
                          | gas_resistance_var['high'], fire_likelihood['high'])

        # Create fuzzy control system
        fire_detection_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
        fire_detector = ctrl.ControlSystemSimulation(fire_detection_ctrl)

        # Fuzzy input values
        fire_detector.input['temperature'] = temperature
        fire_detector.input['humidity'] = humidity
        fire_detector.input['gas_resistance'] = gas_resistance

        # Compute fuzzy output
        fire_detector.compute()

        # Interpret fuzzy output
        fire_likelihood_result = fire_detector.output['fire_likelihood']

        return fire_likelihood_result
