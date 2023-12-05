from internal.contracts.ISensorModel import ISensorModel
from typing import Callable, Any
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

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
            "model_name": "fuzzy_fireDetector",
            "version": "v1.0.0",
            "smcb_wrapper_version": "v1.0.0",
        }
    
    def inferData(self, data: Any, onInfered: Callable[[Any], None], onThresholdExceeded: Callable[[Any], None]):
        onInfered(
            self.fuzzy_danger_level(data["temp"]), 
            self.fuzzy_danger_level(data["gas"]),  # type: ignore
            self.fuzzy_danger_level(data["humid"]), 
            self.fuzzy_danger_level(data["pressure"]))

    def fuzzy_danger_level(self, input_temperature):
        # Membuat variabel input dan output
        temperature = ctrl.Antecedent(np.arange(0, 101, 1), 'temperature')
        danger_level = ctrl.Consequent(np.arange(0, 101, 1), 'danger_level')

        # Mendefinisikan fungsi keanggotaan untuk variabel input dan output
        temperature['low'] = fuzz.trimf(temperature.universe, [0, 0, 50])
        temperature['medium'] = fuzz.trimf(temperature.universe, [0, 50, 100])
        temperature['high'] = fuzz.trimf(temperature.universe, [50, 100, 100])

        danger_level['low'] = fuzz.trimf(danger_level.universe, [0, 0, 50])
        danger_level['medium'] = fuzz.trimf(danger_level.universe, [0, 50, 100])
        danger_level['high'] = fuzz.trimf(danger_level.universe, [50, 100, 100])

        # Menentukan aturan fuzzy
        rule1 = ctrl.Rule(temperature['low'], danger_level['low'])
        rule2 = ctrl.Rule(temperature['medium'], danger_level['medium'])
        rule3 = ctrl.Rule(temperature['high'], danger_level['high'])

        # Membuat sistem kontrol fuzzy
        danger_ctrl = ctrl.ControlSystem([rule1, rule2, rule3])
        danger_level_calc = ctrl.ControlSystemSimulation(danger_ctrl)

        # Memberikan input ke sistem kontrol fuzzy
        danger_level_calc.input['temperature'] = input_temperature

        # Melakukan perhitungan fuzzy
        danger_level_calc.compute()

        # Mengembalikan hasil
        return danger_level_calc.output['danger_level']