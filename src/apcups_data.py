from dataclasses import dataclass, field
import datetime
from typing import Optional


class CommunicationError(Exception):
    ...


@dataclass
class Date:
    raw: int
    value: str = field(init=False)

    def __post_init__(self):
        self.value = self._convert_to_date(self.raw)

    def _convert_to_date(self, days: int) -> datetime:
        return (
            datetime.datetime(2000, 1, 1) + datetime.timedelta(days=days)
        ).isoformat()


@dataclass
class VoltageAcSetting:
    raw: int
    value: str = field(init=False)

    def __post_init__(self):
        self.value = self._convert_voltage_ac_setting(self.raw)

    def _convert_voltage_ac_setting(self, value: int) -> str:
        # sourcery skip: assign-if-exp, move-assign, reintroduce-else,
        # remove-unnecessary-else
        VS_100VAC = 1 << 0
        VS_120VAC = 1 << 1
        VS_200VAC = 1 << 2
        VS_208VAC = 1 << 3
        VS_220VAC = 1 << 4
        VS_230VAC = 1 << 5
        VS_240VAC = 1 << 6

        if value & VS_100VAC:
            return "100"
        if value & VS_120VAC:
            return "120"
        if value & VS_200VAC:
            return "200"
        if value & VS_208VAC:
            return "208"
        if value & VS_220VAC:
            return "220"
        if value & VS_230VAC:
            return "230"
        if value & VS_240VAC:
            return "240"
        else:
            return "Unknown"


@dataclass
class SogRelayConfig:
    raw: int
    value: Optional[dict[str]] = field(init=False)
    mog_presents: Optional[bool] = field(init=False)
    sog0_presents: Optional[bool] = field(init=False)
    sog1_presents: Optional[bool] = field(init=False)
    sog2_presents: Optional[bool] = field(init=False)
    sog3_presents: Optional[bool] = field(init=False)

    def __post_init__(self):
        MOG_PRESENT = 1 << 0
        SOG0_PRESENT = 1 << 1
        SOG1_PRESENT = 1 << 2
        SOG2_PRESENT = 1 << 3
        SOG3_PRESENT = 1 << 4

        self.value = self._convert_sog_relay_config(self.raw)
        self.mog_presents = self.raw & MOG_PRESENT > 0
        self.sog0_presents = self.raw & SOG0_PRESENT > 0
        self.sog1_presents = self.raw & SOG1_PRESENT > 0
        self.sog2_presents = self.raw & SOG2_PRESENT > 0
        self.sog3_presents = self.raw & SOG3_PRESENT > 0

    def _convert_sog_relay_config(self, value: int) -> dict:
        MOG_PRESENT = 1 << 0
        SOG0_PRESENT = 1 << 1
        SOG1_PRESENT = 1 << 2
        SOG2_PRESENT = 1 << 3
        SOG3_PRESENT = 1 << 4

        config = []
        if value & MOG_PRESENT:
            config.append("MOG_Present")
        if value & SOG0_PRESENT:
            config.append("SOG0_Present")
        if value & SOG1_PRESENT:
            config.append("SOG1_Present")
        if value & SOG2_PRESENT:
            config.append("SOG2_Present")
        if value & SOG3_PRESENT:
            config.append("SOG3_Present")
        return config


@dataclass
class UpsStatus:
    raw: int
    value: Optional[dict[str]] = field(init=False)

    def __post_init__(self):
        self.value = self._convert_ups_status(self.raw)

    def _convert_ups_status(self, value: int) -> dict:
        ONLINE = 1 << 1
        ONBATTERY = 1 << 2
        OUTPUTOFF = 1 << 4
        FAULT = 1 << 5
        INPUTBAD = 1 << 6
        TEST = 1 << 7
        PENDING_OUTPUTON = 1 << 8
        PENDING_OUTPUTOFF = 1 << 9
        HIGH_EFFICIENCY = 1 << 13
        INFO_ALERT = 1 << 14

        status = []
        if value & ONLINE:
            status.append("Online")
        if value & ONBATTERY:
            status.append("OnBattery")
        if value & OUTPUTOFF:
            status.append("OutputOff")
        if value & FAULT:
            status.append("Fault")
        if value & INPUTBAD:
            status.append("InputBad")
        if value & TEST:
            status.append("Test")
        if value & PENDING_OUTPUTON:
            status.append("PendingOutputOn")
        if value & PENDING_OUTPUTOFF:
            status.append("PendingOutputOff")
        if value & HIGH_EFFICIENCY:
            status.append("HighEfficiency")
        if value & INFO_ALERT:
            status.append("InformationalAlert")

        return status


@dataclass
class UpsStatusChangeCause:
    raw: int
    value: Optional[dict[str]] = field(init=False)

    def __post_init__(self):
        self.value = self._convert_ups_status_change_cause(self.raw)

    def _convert_ups_status_change_cause(self, value: int) -> dict:
        # sourcery skip: assign-if-exp, low-code-quality, move-assign,
        # reintroduce-else, remove-unnecessary-else
        SYSTEM_INIT = 0
        HIGH_INPUT_VOLTAGE = 1
        LOW_INPUT_VOLTAGE = 2
        DISTORTED_INPUT = 3
        RAPID_CHANGE = 4
        HIGH_INPUT_FREQ = 5
        LOW_INPUT_FREQ = 6
        FREQ_PHASE_DIFF = 7
        ACCEPTABLE_INPUT = 8
        AUTOMATIC_TEST = 9
        TEST_ENDED = 10
        LOCAL_UI_CMD = 11
        PROTOCOL_CMD = 12
        LOW_BATTERY_VOLTAGE = 13
        GENERAL_ERROR = 14
        POWER_SYSTEM_ERROR = 15
        BATTERY_SYSTEM_ERROR = 16
        ERROR_CLEARED = 17
        AUTO_RESTART = 18
        OUTPUT_DISTORTED = 19
        OUTPUT_ACCEPTABLE = 20
        EPO_INTERFACE = 21
        INPUT_PHASE_DELTA_OUT_OF_RANGE = 22
        INPUT_NEUTRAL_DISCONNECTED = 23
        ATS_TRANSFER = 24
        CONFIG_CHANGE = 25
        ALERT_ASSERTED = 26
        ALERT_CLEARED = 27
        PLUG_RATING_EXCEEDED = 28
        OUTLET_GRP_STATE_CHANGE = 29
        FAILURE_BYPASS_EXPIRED = 30

        if value == SYSTEM_INIT:
            return "SystemInitialization"
        if value == HIGH_INPUT_VOLTAGE:
            return "HighInputVoltage"
        if value == LOW_INPUT_VOLTAGE:
            return "LowInputVoltage"
        if value == DISTORTED_INPUT:
            return "DistortedInput"
        if value == RAPID_CHANGE:
            return "RapidChangeOfInputVoltage"
        if value == HIGH_INPUT_FREQ:
            return "HighInputFrequency"
        if value == LOW_INPUT_FREQ:
            return "LowInputFrequency"
        if value == FREQ_PHASE_DIFF:
            return "FrequencyOrPhaseDifference"
        if value == ACCEPTABLE_INPUT:
            return "AcceptableInput"
        if value == AUTOMATIC_TEST:
            return "AutomaticTest"
        if value == TEST_ENDED:
            return "TestEnded"
        if value == LOCAL_UI_CMD:
            return "LocalUICommand"
        if value == PROTOCOL_CMD:
            return "ProtocolCommand"
        if value == LOW_BATTERY_VOLTAGE:
            return "LowBatteryVoltage"
        if value == GENERAL_ERROR:
            return "general_error"
        if value == POWER_SYSTEM_ERROR:
            return "power_system_error"
        if value == BATTERY_SYSTEM_ERROR:
            return "battery_system_error"
        if value == ERROR_CLEARED:
            return "ErrorCleared"
        if value == AUTO_RESTART:
            return "AutomaticRestart"
        if value == OUTPUT_DISTORTED:
            return "DistortedInverterOutput"
        if value == OUTPUT_ACCEPTABLE:
            return "InverterOutputAcceptable"
        if value == EPO_INTERFACE:
            return "EPOInterface"
        if value == INPUT_PHASE_DELTA_OUT_OF_RANGE:
            return "InputPhaseDeltaOutOfRange"
        if value == INPUT_NEUTRAL_DISCONNECTED:
            return "InputNeutralNotConnected"
        if value == ATS_TRANSFER:
            return "ATSTransfer"
        if value == CONFIG_CHANGE:
            return "ConfigurationChange"
        if value == ALERT_ASSERTED:
            return "AlertAsserted"
        if value == ALERT_CLEARED:
            return "AlertCleared"
        if value == PLUG_RATING_EXCEEDED:
            return "PlugRatingExceeded"
        if value == OUTLET_GRP_STATE_CHANGE:
            return "OutletGroupStateChange"
        if value == FAILURE_BYPASS_EXPIRED:
            return "FailureBypassExpired"
        return "Unknown"


@dataclass
class OutletStatus:
    raw: int
    value: Optional[dict[str]] = field(init=False)

    def __post_init__(self):
        self.value = self._convert_outlet_status(self.raw)

    def _convert_outlet_status(self, value: int) -> dict:
        STATE_ON = 1 << 0
        STATE_OFF = 1 << 1
        PROCESS_REBOOT = 1 << 2
        PROCESS_SHUTDOWN = 1 << 3
        PROCESS_SLEEP = 1 << 4
        PEND_OFF_DELAY = 1 << 7
        PEND_ON_AC_PRESENCE = 1 << 8
        PEND_ON_MIN_RUNTIME = 1 << 9
        MEMBER_GROUP_PROC1 = 1 << 10
        MEMBER_GROUP_PROC2 = 1 << 11
        LOW_RUNTIME = 1 << 12

        status = []
        if value & STATE_ON:
            status.append("On")
        if value & STATE_OFF:
            status.append("Off")
        if value & PROCESS_REBOOT:
            status.append("RebootInProgress")
        if value & PROCESS_SHUTDOWN:
            status.append("ShutdownInProgress")
        if value & PROCESS_SLEEP:
            status.append("SleepInProgress")
        if value & PEND_OFF_DELAY:
            status.append("PendingOffDelay")
        if value & PEND_ON_AC_PRESENCE:
            status.append("PendingOnACPresence")
        if value & PEND_ON_MIN_RUNTIME:
            status.append("PendingOnMinRuntime")
        if value & MEMBER_GROUP_PROC1:
            status.append("MemberOfGroup1")
        if value & MEMBER_GROUP_PROC2:
            status.append("MemberOfGroup2")
        if value & LOW_RUNTIME:
            status.append("LowRuntime")
        return status


@dataclass
class SimpleSignalingStatus:
    raw: int
    value: Optional[dict[str]] = field(init=False)

    def __post_init__(self):
        self.value = self._convert_simple_signal_status(self.raw)

    def _convert_simple_signal_status(self, value: int) -> dict:
        POWER_FAILURE = 1 << 0
        SHUTDOWN_IMMINENT = 1 << 1

        status = []
        if value & POWER_FAILURE:
            status.append("PowerFailure")
        if value & SHUTDOWN_IMMINENT:
            status.append("ShutdownImminent")
        return status


@dataclass
class GeneralError:
    raw: int
    value: Optional[dict[str]] = field(init=False)

    def __post_init__(self):
        self.value = self._convert_general_error(self.raw)

    def _convert_general_error(self, value: int) -> dict:
        SITE_WIRING = 1 << 0
        EEPROM = 1 << 1
        ADC = 1 << 2
        LOGIC_PS = 1 << 3
        INTERNAL_COMMS = 1 << 4
        UI_BUTTON = 1 << 5
        EPO_ACTIVE = 1 << 7

        status = []
        if value & SITE_WIRING:
            status.append("SiteWiringFault")
        if value & EEPROM:
            status.append("EEPROM_Fault")
        if value & ADC:
            status.append("ADConverterFault")
        if value & LOGIC_PS:
            status.append("LogicPowerSupplyFault")
        if value & INTERNAL_COMMS:
            status.append("InternalCommunicationFault")
        if value & UI_BUTTON:
            status.append("UIButtonFault")
        if value & EPO_ACTIVE:
            status.append("EmergencyPowerOffActive")
        return status


@dataclass
class PowerSystemError:
    raw: int
    value: Optional[dict[str]] = field(init=False)

    def __post_init__(self):
        self.value = self._convert_power_system_error(self.raw)

    def _convert_power_system_error(self, value: int) -> dict:
        OUTPUT_OVERLOAD = 1 << 0
        OUTPUT_SHORT = 1 << 1
        OUTPUT_OVERVOLT = 1 << 2
        OUTPUT_OVERTEMP = 1 << 4
        BACKFEED_RELAY = 1 << 5
        AVR_RELAY = 1 << 6
        PFCINPUT_RELAY = 1 << 7
        OUTPUT_RELAY = 1 << 8
        BYPASS_RELAY = 1 << 9
        PFC = 1 << 11
        DC_BUS_OVERVOLT = 1 << 12
        INVERTER = 1 << 13

        status = []
        if value & OUTPUT_OVERLOAD:
            status.append("OutputOverload")
        if value & OUTPUT_SHORT:
            status.append("OutputShortCircuit")
        if value & OUTPUT_OVERVOLT:
            status.append("OutputOvervoltage")
        if value & OUTPUT_OVERTEMP:
            status.append("OutputOverTemperature")
        if value & BACKFEED_RELAY:
            status.append("BackfeedRelayFault")
        if value & AVR_RELAY:
            status.append("AVRRelayFault")
        if value & PFCINPUT_RELAY:
            status.append("PFCInputRelayFault")
        if value & OUTPUT_RELAY:
            status.append("OutputRelayFault")
        if value & BYPASS_RELAY:
            status.append("BypassRelayFault")
        if value & PFC:
            status.append("PFCFault")
        if value & DC_BUS_OVERVOLT:
            status.append("DCBusOvervoltage")
        if value & INVERTER:
            status.append("InverterFault")
        return status


@dataclass
class BatterySystemError:
    raw: int
    value: Optional[dict[str]] = field(init=False)

    def __post_init__(self):
        self.value = self._convert_battery_system_error(self.raw)

    def _convert_battery_system_error(self, value: int) -> dict:
        DISCONNECTED = 1 << 0
        OVERVOLT = 1 << 1
        NEEDS_REPLACEMENT = 1 << 2
        OVERTEMP = 1 << 3
        CHARGER = 1 << 4
        TEMP_SENSOR = 1 << 5
        BUS_SOFT_START = 1 << 6

        status = []
        if value & DISCONNECTED:
            status.append("BatteryDisconnected")
        if value & OVERVOLT:
            status.append("Overvoltage")
        if value & NEEDS_REPLACEMENT:
            status.append("NeedsReplacement")
        if value & OVERTEMP:
            status.append("OverTemperature")
        if value & CHARGER:
            status.append("ChargerFault")
        if value & TEMP_SENSOR:
            status.append("TemperatureSensorFault")
        if value & BUS_SOFT_START:
            status.append("BusSoftStartFault")
        return status


@dataclass
class ReplaceBatteryTestStatus:
    raw: int
    value: Optional[dict[str]] = field(init=False)

    def __post_init__(self):
        self.value = self._convert_replace_battery_test_status(self.raw)

    def _convert_replace_battery_test_status(self, value: int) -> dict:
        PENDING = 1 << 0
        IN_PROGRESS = 1 << 1
        PASSED = 1 << 2
        FAILED = 1 << 3
        REFUSED = 1 << 4
        ABORTED = 1 << 5
        SRC_PROTOCOL = 1 << 6
        SRC_LOCAL_UI = 1 << 7
        SRC_INTERNAL = 1 << 8
        INVALID_STATE = 1 << 9
        INTERNAL_FAULT = 1 << 10
        STATE_OF_CHARGE = 1 << 11

        status = []
        if value & PENDING:
            status.append("Pending")
        if value & IN_PROGRESS:
            status.append("InProgress")
        if value & PASSED:
            status.append("Passed")
        if value & FAILED:
            status.append("Failed")
        if value & REFUSED:
            status.append("Refused")
        if value & ABORTED:
            status.append("Aborted")
        if value & SRC_PROTOCOL:
            status.append("SourceProtocol")
        if value & SRC_LOCAL_UI:
            status.append("SourceLocalUI")
        if value & SRC_INTERNAL:
            status.append("SourceInternal")
        if value & INVALID_STATE:
            status.append("InvalidState")
        if value & INTERNAL_FAULT:
            status.append("InternalFault")
        if value & STATE_OF_CHARGE:
            status.append("StateOfChargeNotAcceptable")
        return status


@dataclass
class RuntimeCalibrationStatus:
    raw: int
    value: Optional[dict[str]] = field(init=False)

    def __post_init__(self):
        self.value = self._convert_runtime_calibration_status(self.raw)

    def _convert_runtime_calibration_status(self, value: int) -> dict:
        PENDING = 1 << 0
        IN_PROGRESS = 1 << 1
        PASSED = 1 << 2
        FAILED = 1 << 3
        REFUSED = 1 << 4
        ABORTED = 1 << 5
        SRC_PROTOCOL = 1 << 6
        SRC_LOCAL_UI = 1 << 7
        SRC_INTERNAL = 1 << 8
        INVALID_STATE = 1 << 9
        INTERNAL_FAULT = 1 << 10
        STATE_OF_CHARGE = 1 << 11
        LOAD_CHANGE = 1 << 12
        AC_INPUT_BAD = 1 << 13
        LOAD_TOO_LOW = 1 << 14
        OVER_CHARGE = 1 << 15

        status = []
        if value & PENDING:
            status.append("Pending")
        if value & IN_PROGRESS:
            status.append("InProgress")
        if value & PASSED:
            status.append("Passed")
        if value & FAILED:
            status.append("Failed")
        if value & REFUSED:
            status.append("Refused")
        if value & ABORTED:
            status.append("Aborted")
        if value & SRC_PROTOCOL:
            status.append("SourceProtocol")
        if value & SRC_LOCAL_UI:
            status.append("SourceLocalUI")
        if value & SRC_INTERNAL:
            status.append("SourceInternal")
        if value & INVALID_STATE:
            status.append("InvalidState")
        if value & INTERNAL_FAULT:
            status.append("InternalFault")
        if value & STATE_OF_CHARGE:
            status.append("StateOfChargeNotAcceptable")
        if value & LOAD_CHANGE:
            status.append("LoadChange")
        if value & AC_INPUT_BAD:
            status.append("ACInputBad")
        if value & LOAD_TOO_LOW:
            status.append("LoadTooLow")
        if value & OVER_CHARGE:
            status.append("OverCharge")
        return status


@dataclass
class BatteryLifeTimeStatus:
    raw: int
    value: Optional[dict[str]] = field(init=False)

    def __post_init__(self):
        self.value = self._convert_battery_life_time_status(self.raw)

    def _convert_battery_life_time_status(self, value: int) -> dict:
        OK = 1 << 0
        NEAR_END = 1 << 1
        EXCEEDED = 1 << 2
        NEAR_END_ACK = 1 << 3
        EXCEEDED_ACK = 1 << 4

        status = []
        if value & OK:
            status.append("OK")
        if value & NEAR_END:
            status.append("NearEnd")
        if value & EXCEEDED:
            status.append("Exceeded")
        if value & NEAR_END_ACK:
            status.append("NearEndAcknowledged")
        if value & EXCEEDED_ACK:
            status.append("ExceededAcknowledged")
        return status


@dataclass
class UserInterfaceStatus:
    raw: int
    value: Optional[dict[str]] = field(init=False)

    def __post_init__(self):
        self.value = self._convert_user_interface_status(self.raw)

    def _convert_user_interface_status(self, value: int) -> dict:
        TEST_IN_PROGRESS = 1 << 0
        AUDIBLE_ALARM = 1 << 1
        ALARM_MUTED = 1 << 2

        status = []
        if value & TEST_IN_PROGRESS:
            status.append("ContinuousTestInProgress")
        if value & AUDIBLE_ALARM:
            status.append("AudibleAlarmInProgress")
        if value & ALARM_MUTED:
            status.append("AudibleAlarmMuted")
        return status


@dataclass
class InputStatus:
    raw: int
    value: Optional[dict[str]] = field(init=False)

    def __post_init__(self):
        self.value = self._convert_input_status(self.raw)

    def _convert_input_status(self, value: int) -> dict:
        ACCEPTABLE = 1 << 0
        PENDING_ACCEPTABLE = 1 << 1
        LOW_VOLTAGE = 1 << 2
        HIGH_VOLTAGE = 1 << 3
        DISTORTED = 1 << 4
        BOOST = 1 << 5
        TRIM = 1 << 6
        LOW_FREQ = 1 << 7
        HIGH_FREQ = 1 << 8
        FREQ_PHASE_UNLOCKED = 1 << 9

        status = []
        if value & ACCEPTABLE:
            status.append("Acceptable")
        if value & PENDING_ACCEPTABLE:
            status.append("PendingAcceptable")
        if value & LOW_VOLTAGE:
            status.append("VoltageTooLow")
        if value & HIGH_VOLTAGE:
            status.append("VoltageTooHigh")
        if value & DISTORTED:
            status.append("Distorted")
        if value & BOOST:
            status.append("Boost")
        if value & TRIM:
            status.append("Trim")
        if value & LOW_FREQ:
            status.append("FrequencyTooLow")
        if value & HIGH_FREQ:
            status.append("FrequencyTooHigh")
        if value & FREQ_PHASE_UNLOCKED:
            status.append("FrequencyPhaseNotLocked")
        return status


@dataclass
class InputEfficiency:
    raw: int
    value: Optional[int | str] = field(init=False)

    def __post_init__(self):
        efficiency = self.raw / 128 if self.raw > 0 else self.raw
        self.value = self._convert_input_efficiency(self.raw)
        self.raw = efficiency

    def _convert_input_efficiency(self, value: int) -> int | str:
        if value == -1:
            return "NotAvailable"
        elif value == -2:
            return "LoadTooLow"
        elif value == -3:
            return "OutputOff"
        elif value == -4:
            return "OnBattery"
        elif value == -5:
            return "InBypass"
        elif value == -6:
            return "BatteryCharging"
        elif value == -7:
            return "PoorACInput"
        elif value == -8:
            return "BatteryDisconnected"
        else:
            return round(value / 128, 1)


@dataclass
class CoutdownCounter:
    raw: int
    value: Optional[int | str] = field(init=False)

    def __post_init__(self):
        self.value = self._convert_coutdown_counter(self.raw)

    def _convert_coutdown_counter(self, value) -> int | str:
        if value == -1:
            return "NotActive"
        elif value == 0:
            return "CountdownExpired"
        else:
            return value


@dataclass
class BatteryTestIntervalSetting:
    raw: int
    value: Optional[dict[str]] = field(init=False)

    def __post_init__(self):
        self.value = self._convert_battery_test_interval_setting(self.raw)

    def _convert_battery_test_interval_setting(self, value: int) -> dict:
        NEVER = 1 << 0
        ONSTARTUPONLY = 1 << 1
        ONSTARTUPPLUS7 = 1 << 2
        ONSTARTUPPLUS14 = 1 << 3
        ONSTARTUP7SINCE = 1 << 4
        ONSTARTUP14SINCE = 1 << 5

        command = []
        if value & NEVER:
            command.append("Never")
        if value & ONSTARTUPONLY:
            command.append("OnStartUpOnly")
        if value & ONSTARTUPPLUS7:
            command.append("OnStartUpPlus7")
        if value & ONSTARTUPPLUS14:
            command.append("OnStartUpPlus14")
        if value & ONSTARTUP7SINCE:
            command.append("OnStartUp7Since")
        if value & ONSTARTUP14SINCE:
            command.append("OnStartUp14Since")
        return command


@dataclass
class OutputSensitivitySetting:
    raw: int
    value: Optional[int | str] = field(init=False)

    def __post_init__(self):
        self.value = self._convert_output_sensitivity_setting(self.raw)

    def _convert_output_sensitivity_setting(self, value: int) -> int | str:
        NORMAL = 1 << 0
        REDUCED = 1 << 1
        LOW = 1 << 2

        command = []
        if value & NORMAL:
            command.append("Normal")
        if value & REDUCED:
            command.append("Reduced")
        if value & LOW:
            command.append("Low")
        return command


@dataclass
class Upsdommand:
    raw: int
    value: Optional[dict[str]] = field(init=False)

    def __post_init__(self):
        self.value = self._convert_ups_command(self.raw)

    def _convert_ups_command(self, value: int) -> dict:
        RESTORE_FACT_SETTINGS = 1 << 3

        command = []
        if value & RESTORE_FACT_SETTINGS:
            command.append("RestoreFactorySettings")
        return command


@dataclass
class OutletCommand:
    raw: int
    value: Optional[dict[str]] = field(init=False)

    def __post_init__(self):
        self.value = self._convert_outlet_command(self.raw)

    def _convert_outlet_command(self, value: int) -> dict:
        CANCEL = 1 << 0
        OUTPUT_ON = 1 << 1
        OUTPUT_OFF = 1 << 2
        OUTPUT_SHUTDOWN = 1 << 3
        OUTPUT_REBOOT = 1 << 4
        COLD_BOOT_ALLOWED = 1 << 5
        USE_ON_DELAY = 1 << 6
        USE_OFF_DELAY = 1 << 7
        TARGET_UOG = 1 << 8
        TARGET_SOG0 = 1 << 9
        TARGET_SOG1 = 1 << 10
        TARGET_SOG2 = 1 << 11
        SRC_USB = 1 << 12
        SRC_LOCAL_UI = 1 << 13
        SRC_RJ45 = 1 << 14
        SRC_SMARTSLOT1 = 1 << 15

        status = []
        if value & CANCEL:
            status.append("Cancel")
        if value & OUTPUT_ON:
            status.append("OutputOn")
        if value & OUTPUT_OFF:
            status.append("OutputOff")
        if value & OUTPUT_SHUTDOWN:
            status.append("OutputShutdown")
        if value & OUTPUT_REBOOT:
            status.append("OutputReboot")
        if value & COLD_BOOT_ALLOWED:
            status.append("ColdBootAllowed")
        if value & USE_ON_DELAY:
            status.append("UseOnDelay")
        if value & USE_OFF_DELAY:
            status.append("UseOffDelay")
        if value & TARGET_UOG:
            status.append("UnswitchedOutletGroup")
        if value & TARGET_SOG0:
            status.append("SwitchedOutletGroup0")
        if value & TARGET_SOG1:
            status.append("SwitchedOutletGroup1")
        if value & TARGET_SOG2:
            status.append("SwitchedOutletGroup2")
        if value & SRC_USB:
            status.append("SourceUSBPort")
        if value & SRC_LOCAL_UI:
            status.append("SourceLocalUI")
        if value & SRC_RJ45:
            status.append("SourceRJ45")
        if value & SRC_SMARTSLOT1:
            status.append("SourceSmartSlot1")
        return status


@dataclass
class SimpleSignalingCommand:
    raw: int
    value: Optional[dict[str]] = field(init=False)

    def __post_init__(self):
        self.value = self._convert_simple_signaling_command(self.raw)

    def _convert_simple_signaling_command(self, value: int) -> dict:
        REQUEST_SHUTDOWN = 1 << 0
        REMOTE_OFF = 1 << 1
        REMOTE_ON = 1 << 2

        status = []
        if value & REQUEST_SHUTDOWN:
            status.append("RequestShutdown")
        if value & REMOTE_OFF:
            status.append("RemoteOff")
        if value & REMOTE_ON:
            status.append("RemoteOn")
        return status


@dataclass
class ReplaceBatteryTestCommand:
    raw: int
    value: Optional[dict[str]] = field(init=False)

    def __post_init__(self):
        self.value = self._convert_replace_battery_test_command(self.raw)

    def _convert_replace_battery_test_command(self, value: int) -> dict:
        START = 1 << 0
        ABORT = 1 << 1

        command = []
        if value & START:
            command.append("Start")
        if value & ABORT:
            command.append("Abort")
        return command


@dataclass
class RuntimeCalibrationCommand:
    raw: int
    value: Optional[dict[str]] = field(init=False)

    def __post_init__(self):
        self.value = self._convert_runtime_calibration_command(self.raw)

    def _convert_runtime_calibration_command(self, value: int) -> dict:
        START_CALIBRATION = 0 << 0
        ABORT_CALIBRATION = 1 << 1

        command = []
        if value & START_CALIBRATION:
            command.append("StartCalibration")
        if value & ABORT_CALIBRATION:
            command.append("AbortCalibration")
        return command


@dataclass
class UserInterfaceCommand:
    raw: int
    value: Optional[dict[str]] = field(init=False)

    def __post_init__(self):
        self.value = self._convert_user_interface_command(self.raw)

    def _convert_user_interface_command(self, value: int) -> dict:
        SHORT_TEST = 1 << 0
        CONTINUOUS_TEST = 1 << 1
        MUTE_ALARMS = 1 << 2
        UNMUTE_ALARMS = 1 << 3
        ACK_BATTERY_ALARMS = 1 << 5

        command = []
        if value & SHORT_TEST:
            command.append("ShortTest")
        if value & CONTINUOUS_TEST:
            command.append("ContinuousTest")
        if value & MUTE_ALARMS:
            command.append("MuteAllActiveAudibleAlarms")
        if value & UNMUTE_ALARMS:
            command.append("CancelMute")
        if value & ACK_BATTERY_ALARMS:
            command.append("AcknowledgeBatteryAlarms")
        return command


@dataclass
class InventoryData:
    fw_version: str
    model: str
    sku: str
    serial_number: str
    battery_sku: str
    external_battery_sku: str
    output_apparent_power_rating: int
    output_real_power_rating: int
    sog_relay_config_setting: SogRelayConfig
    manufcturing_date: Date
    output_voltage_ac_setting: VoltageAcSetting
    battery_installation_date: Date
    name: str
    mog_name: str
    sog0_name: str
    sog1_name: str
    sog2_name: str


@dataclass
class StatusData:
    ups_status_change_cause: UpsStatusChangeCause
    ups_status: UpsStatus
    mog_outlet_status: OutletStatus
    sog0_outlet_status: OutletStatus
    sog1_outlet_status: OutletStatus
    sog2_outlet_status: OutletStatus
    sog3_outlet_status: OutletStatus
    simple_signaling_status: SimpleSignalingStatus
    general_error: GeneralError
    power_system_error: PowerSystemError
    battery_system_error: BatterySystemError
    replace_battery_test_status: ReplaceBatteryTestStatus
    runtime_calibration_status: RuntimeCalibrationStatus
    battery_life_time_status: BatteryLifeTimeStatus
    user_interface_status: UserInterfaceStatus


@dataclass
class DynamicData:
    runtime_remaining_s: int
    state_of_charge_pct: float
    battery_positive_voltage_dc: float
    battery_negative_voltage_dc: float
    battery_replacement_date: Date
    battery_temperature: float
    output0_real_power_pct: float
    output0_apparent_power_pct: float
    output0_current_ac: float
    output0_voltage_ac: float
    output_frequency: float
    output_energy_kwh: float
    input0_voltage_ac: float
    input_efficiency: InputEfficiency
    mog_turn_off_countdown: CoutdownCounter
    mog_turn_on_countdown: CoutdownCounter
    mog_stay_off_countdown: CoutdownCounter
    sog0_turn_off_countdown: CoutdownCounter
    sog0_turn_on_countdown: CoutdownCounter
    sog0_stay_off_countdown: CoutdownCounter
    sog1_turn_off_countdown: CoutdownCounter
    sog1_turn_on_countdown: CoutdownCounter
    sog1_stay_off_countdown: CoutdownCounter
    sog2_turn_off_countdown: CoutdownCounter
    sog2_turn_on_countdown: CoutdownCounter
    sog2_stay_off_countdown: CoutdownCounter
    sog3_turn_off_countdown: CoutdownCounter
    sog3_turn_on_countdown: CoutdownCounter
    sog3_stay_off_countdown: CoutdownCounter
    output0_apparent_power_va: float
    output0_real_power_w: float
    input_status: InputStatus
    runtime_remaining_min: int


@dataclass
class Settings:
    output_upper_acceptable_voltage_setting: int
    output_lower_acceptable_voltage_setting: int
    mog_turn_off_countdown_setting: int
    mog_turn_on_countdown_setting: int
    mog_stay_off_countdown_setting: int
    mog_minimum_return_runtime_setting: int
    sog0_turn_off_countdown_setting: int
    sog0_turn_on_countdown_setting: int
    sog0_stay_off_countdown_setting: int
    sog0_minimum_return_runtime_setting: int
    sog1_turn_off_countdown_setting: int
    sog1_turn_on_countdown_setting: int
    sog1_stay_off_countdown_setting: int
    sog1_minimum_return_runtime_setting: int
    sog2_turn_off_countdown_setting: int
    sog2_turn_on_countdown_setting: int
    sog2_stay_off_countdown_setting: int
    sog2_minimum_return_runtime_setting: int
    sog3_turn_off_countdown_setting: int
    sog3_turn_on_countdown_setting: int
    sog3_stay_off_countdown_setting: int
    sog3_minimum_return_runtime_setting: int
    battery_test_interval_setting: BatteryTestIntervalSetting
    output_sensitivity_setting: OutputSensitivitySetting


@dataclass
class CommandsData:
    ups_command: Upsdommand
    outlet_command: OutletCommand
    simple_signaling_command: SimpleSignalingCommand
    replace_battery_test_command: ReplaceBatteryTestCommand
    run_time_calibration_command: RuntimeCalibrationCommand
    user_interface_command: UserInterfaceCommand


@dataclass
class VerificationData:
    modbus_map_ID: str
    test_string: str
    test_number1: int
    test_number2: int
    test_2b_number1: int
    test_2b_number2: int
    test_bpin_number1: float
    test_bpin_number2: float
