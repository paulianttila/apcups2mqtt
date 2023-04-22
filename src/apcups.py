import logging
from apcups_data import (
    BatteryLifeTimeStatus,
    BatterySystemError,
    BatteryTestIntervalSetting,
    CommandsData,
    CommunicationError,
    Date,
    DynamicData,
    GeneralError,
    InputEfficiency,
    InputStatus,
    InventoryData,
    OutletCommand,
    OutletStatus,
    OutputSensitivitySetting,
    PowerSystemError,
    ReplaceBatteryTestCommand,
    ReplaceBatteryTestStatus,
    RuntimeCalibrationCommand,
    RuntimeCalibrationStatus,
    Settings,
    SimpleSignalingCommand,
    SimpleSignalingStatus,
    SogRelayConfig,
    StatusData,
    UpsStatus,
    UpsStatusChangeCause,
    Upsdommand,
    UserInterfaceCommand,
    UserInterfaceStatus,
    VerificationData,
    VoltageAcSetting,
)
from pyModbusTCP.client import ModbusClient
from pymodbus.payload import BinaryPayloadDecoder
from pymodbus.constants import Endian


class ApcUps:
    def __init__(
        self,
        host: str,
        port: int = 502,
        auto_open=True,
        auto_close=False,
        debug: bool = False,
        logger=None,
    ):
        self.logger = logger or logging.getLogger(__name__)
        self.client = ModbusClient(
            host=host,
            port=port,
            unit_id=1,
            auto_open=auto_open,
            auto_close=auto_close,
            debug=debug,
        )
        self.inventory_data = None
        self.status_data = None
        self.dynamic_data = None
        self.static_data = None
        self.commands_data = None
        self.mog_present = False
        self.sog0_present = False
        self.sog1_present = False
        self.sog2_present = False
        self.sog3_present = False

    def open_connection(self) -> None:
        self.client.open()

    def close_connection(self) -> None:
        self.client.close()

    def _fetch_data(self, addr: int, reg_nb: int) -> list[int] | None:
        if result := self.client.read_holding_registers(addr, reg_nb):
            self.logger.debug(f"addr: {addr}, reg_nb: {reg_nb}, result: {result}")
            return result
        raise CommunicationError(f"Failed to fetch {reg_nb} regs from address {addr}")

    def _convert_to_str(self, val: str) -> str:
        return val.decode("ascii", errors="ignore").rstrip("\x00").strip(" ")

    def _get_data_as_decoder(
        self, addr: int, reg_nb: int
    ) -> BinaryPayloadDecoder | None:
        result = self._fetch_data(addr, reg_nb)
        return BinaryPayloadDecoder.fromRegisters(result, byteorder=Endian.Big)

    def fetch_inventory_data(self) -> InventoryData:
        decoder = self._get_data_as_decoder(516, 88)
        fw_version = self._convert_to_str(decoder.decode_string(16))  # 516
        decoder.skip_bytes(16)  # 524
        model = self._convert_to_str(decoder.decode_string(32))  # 532
        sku = self._convert_to_str(decoder.decode_string(32))  # 548
        serial_number = self._convert_to_str(decoder.decode_string(16))  # 564
        battery_sku = self._convert_to_str(decoder.decode_string(16))  # 572
        external_battery_sku = self._convert_to_str(decoder.decode_string(16))  # 580
        output_apparent_power_rating = decoder.decode_16bit_uint()  # 588
        output_real_power_rating = decoder.decode_16bit_uint()  # 589
        sog_relay_config_setting_bf = decoder.decode_16bit_uint()  # 590
        manufcturing_date_int = decoder.decode_16bit_uint()  # 591
        output_voltage_ac_setting_bf = decoder.decode_16bit_uint()  # 592
        decoder.skip_bytes(4)  # 593
        battery_installation_date_int = decoder.decode_16bit_uint()  # 595
        name = self._convert_to_str(decoder.decode_string(16))  # 596

        decoder = self._get_data_as_decoder(604, 64)
        mog_name = self._convert_to_str(decoder.decode_string(16))  # 604
        sog0_name = self._convert_to_str(decoder.decode_string(16))  # 612
        sog1_name = self._convert_to_str(decoder.decode_string(16))  # 620
        sog2_name = self._convert_to_str(decoder.decode_string(16))  # 628

        battery_installation_date = Date(battery_installation_date_int)
        manufcturing_date = Date(manufcturing_date_int)

        output_voltage_ac_setting = VoltageAcSetting(output_voltage_ac_setting_bf)
        sog_relay_config_setting = SogRelayConfig(sog_relay_config_setting_bf)
        self.mog_present = sog_relay_config_setting.mog_presents
        self.sog0_present = sog_relay_config_setting.sog0_presents
        self.sog1_present = sog_relay_config_setting.sog1_presents
        self.sog2_present = sog_relay_config_setting.sog2_presents
        self.sog3_present = sog_relay_config_setting.sog3_presents

        self.inventory_data = InventoryData(
            fw_version=fw_version,
            model=model,
            sku=sku,
            serial_number=serial_number,
            battery_sku=battery_sku,
            external_battery_sku=external_battery_sku,
            output_apparent_power_rating=output_apparent_power_rating,
            output_real_power_rating=output_real_power_rating,
            manufcturing_date=manufcturing_date,
            battery_installation_date=battery_installation_date,
            name=name,
            mog_name=mog_name,
            sog0_name=sog0_name,
            sog1_name=sog1_name,
            sog2_name=sog2_name,
            output_voltage_ac_setting=output_voltage_ac_setting,
            sog_relay_config_setting=sog_relay_config_setting,
        )
        return self.inventory_data

    def fetch_status_data(self) -> StatusData:
        if self.inventory_data is None:
            self.fetch_inventory_data()

        decoder = self._get_data_as_decoder(0, 27)
        ups_status_bf = decoder.decode_32bit_uint()  # 0
        ups_status_change_cause_bf = decoder.decode_16bit_uint()  # 2
        mog_outlet_status_bf = decoder.decode_32bit_uint()  # 3
        decoder.skip_bytes(2)  # 5
        sog0_outlet_status_bf = decoder.decode_32bit_uint()  # 6
        decoder.skip_bytes(2)  # 8
        sog1_outlet_status_bf = decoder.decode_32bit_uint()  # 9
        decoder.skip_bytes(2)  # 11
        sog2_outlet_status_bf = decoder.decode_32bit_uint()  # 12
        decoder.skip_bytes(2)  # 14
        sog3_outlet_status_bf = decoder.decode_32bit_uint()  # 15
        decoder.skip_bytes(2)  # 17
        simple_signaling_status_bf = decoder.decode_16bit_uint()  # 18
        general_error_bf = decoder.decode_16bit_uint()  # 19
        power_system_error_bf = decoder.decode_32bit_uint()  # 20, 21
        battery_system_error_bf = decoder.decode_16bit_uint()  # 22
        replace_battery_test_status_bf = decoder.decode_16bit_uint()  # 23
        runtime_calibration_status_bf = decoder.decode_16bit_uint()  # 24
        battery_life_time_status_bf = decoder.decode_16bit_uint()  # 25
        user_interface_status_bf = decoder.decode_16bit_uint()  # 26

        ups_status = UpsStatus(ups_status_bf)
        ups_status_change_cause = UpsStatusChangeCause(ups_status_change_cause_bf)

        mog_outlet_status = None
        if self.mog_present:
            mog_outlet_status = OutletStatus(mog_outlet_status_bf)

        sog0_outlet_status = None
        if self.sog0_present:
            sog0_outlet_status = OutletStatus(sog0_outlet_status_bf)

        sog1_outlet_status = None
        if self.sog1_present:
            sog1_outlet_status = OutletStatus(sog1_outlet_status_bf)

        sog2_outlet_status = None
        if self.sog2_present:
            sog2_outlet_status = OutletStatus(sog2_outlet_status_bf)

        sog3_outlet_status = None
        if self.sog3_present:
            sog3_outlet_status = OutletStatus(sog3_outlet_status_bf)

        simple_signaling_status = SimpleSignalingStatus(simple_signaling_status_bf)
        general_error = GeneralError(general_error_bf)
        power_system_error = PowerSystemError(power_system_error_bf)
        battery_system_error = BatterySystemError(battery_system_error_bf)
        replace_battery_test_status = ReplaceBatteryTestStatus(
            replace_battery_test_status_bf
        )
        runtime_calibration_status = RuntimeCalibrationStatus(
            runtime_calibration_status_bf
        )
        battery_life_time_status = BatteryLifeTimeStatus(battery_life_time_status_bf)
        user_interface_status = UserInterfaceStatus(user_interface_status_bf)

        return StatusData(
            ups_status_change_cause=ups_status_change_cause,
            ups_status=ups_status,
            mog_outlet_status=mog_outlet_status,
            sog0_outlet_status=sog0_outlet_status,
            sog1_outlet_status=sog1_outlet_status,
            sog2_outlet_status=sog2_outlet_status,
            sog3_outlet_status=sog3_outlet_status,
            simple_signaling_status=simple_signaling_status,
            general_error=general_error,
            power_system_error=power_system_error,
            battery_system_error=battery_system_error,
            replace_battery_test_status=replace_battery_test_status,
            runtime_calibration_status=runtime_calibration_status,
            battery_life_time_status=battery_life_time_status,
            user_interface_status=user_interface_status,
        )

    def fetch_dynamic_data(self) -> DynamicData:
        if self.inventory_data is None:
            self.fetch_inventory_data()

        decoder = self._get_data_as_decoder(128, 54)
        runtime_remaining_s = decoder.decode_32bit_uint()  # 128
        state_of_charge_pct = decoder.decode_16bit_uint() / 512  # 130
        battery_positive_voltage_dc = decoder.decode_16bit_int() / 32  # 131
        battery_negative_voltage_dc = decoder.decode_16bit_int() / 32  # 132
        battery_replacement_date_int = decoder.decode_16bit_uint()  # 133
        decoder.skip_bytes(2),  # 134
        battery_temperature = decoder.decode_16bit_int() / 128  # 135
        output0_real_power_pct = decoder.decode_16bit_uint() / 256  # 136
        decoder.skip_bytes(2)  # 137
        output0_apparent_power_pct = decoder.decode_16bit_uint() / 256  # 138
        decoder.skip_bytes(2)  # 139
        output0_current_ac = decoder.decode_16bit_uint() / 32  # 140
        decoder.skip_bytes(2)  # 141
        output0_voltage_ac = decoder.decode_16bit_uint() / 64  # 142
        decoder.skip_bytes(2)  # 143
        output_frequency = decoder.decode_16bit_uint() / 128  # 144
        output_energy_kwh = decoder.decode_32bit_uint() / 1000  # 145
        decoder.skip_bytes(6)  # 147
        input_status_bf = decoder.decode_16bit_uint()  # 150
        input0_voltage_ac = decoder.decode_16bit_uint() / 64  # 151
        decoder.skip_bytes(4)  # 152
        input_efficiency_raw = decoder.decode_16bit_int()  # 154
        mog_turn_off_countdown = decoder.decode_16bit_int()  # 155
        mog_turn_on_countdown = decoder.decode_16bit_int()  # 156
        mog_stay_off_countdown = decoder.decode_32bit_int()  # 157
        sog0_turn_off_countdown = decoder.decode_16bit_int()  # 159
        sog0_turn_on_countdown = decoder.decode_16bit_int()  # 160
        sog0_stay_off_countdown = decoder.decode_32bit_int()  # 161
        sog1_turn_off_countdown = decoder.decode_16bit_int()  # 163
        sog1_turn_on_countdown = decoder.decode_16bit_int()  # 164
        sog1_stay_off_countdown = decoder.decode_32bit_int()  # 165
        sog2_turn_off_countdown = decoder.decode_16bit_int()  # 167
        sog2_turn_on_countdown = decoder.decode_16bit_int()  # 168
        sog2_stay_off_countdown = decoder.decode_32bit_int()  # 169
        sog3_turn_off_countdown = decoder.decode_16bit_int()  # 171
        sog3_turn_on_countdown = decoder.decode_16bit_int()  # 172
        sog3_stay_off_countdown = decoder.decode_32bit_int()  # 173

        input_status = InputStatus(input_status_bf)
        runtime_remaining_min = runtime_remaining_s / 60
        battery_replacement_date = Date(battery_replacement_date_int)
        output0_apparent_power_va = self._calculate_apparent_power(
            output0_apparent_power_pct
        )
        output0_real_power_w = self._calculate_real_power(output0_real_power_pct)
        input_efficiency = InputEfficiency(input_efficiency_raw)

        self.dynamic_data = DynamicData(
            runtime_remaining_s=runtime_remaining_s,
            state_of_charge_pct=state_of_charge_pct,
            battery_positive_voltage_dc=battery_positive_voltage_dc,
            battery_negative_voltage_dc=battery_negative_voltage_dc,
            battery_replacement_date=battery_replacement_date,
            battery_temperature=battery_temperature,
            output0_real_power_pct=output0_real_power_pct,
            output0_apparent_power_pct=output0_apparent_power_pct,
            output0_current_ac=output0_current_ac,
            output0_voltage_ac=output0_voltage_ac,
            output_frequency=output_frequency,
            output_energy_kwh=output_energy_kwh,
            input0_voltage_ac=input0_voltage_ac,
            input_efficiency=input_efficiency,
            mog_turn_off_countdown=mog_turn_off_countdown,
            mog_turn_on_countdown=mog_turn_on_countdown,
            mog_stay_off_countdown=mog_stay_off_countdown,
            sog0_turn_off_countdown=sog0_turn_off_countdown,
            sog0_turn_on_countdown=sog0_turn_on_countdown,
            sog0_stay_off_countdown=sog0_stay_off_countdown,
            sog1_turn_off_countdown=sog1_turn_off_countdown,
            sog1_turn_on_countdown=sog1_turn_on_countdown,
            sog1_stay_off_countdown=sog1_stay_off_countdown,
            sog2_turn_off_countdown=sog2_turn_off_countdown,
            sog2_turn_on_countdown=sog2_turn_on_countdown,
            sog2_stay_off_countdown=sog2_stay_off_countdown,
            sog3_turn_off_countdown=sog3_turn_off_countdown,
            sog3_turn_on_countdown=sog3_turn_on_countdown,
            sog3_stay_off_countdown=sog3_stay_off_countdown,
            output0_apparent_power_va=output0_apparent_power_va,
            output0_real_power_w=output0_real_power_w,
            input_status=input_status,
            runtime_remaining_min=runtime_remaining_min,
        )
        self._set_dynamic_data_sogs(self.dynamic_data)
        return self.dynamic_data

    def _set_dynamic_data_sogs(self, data: DynamicData) -> DynamicData:
        if self.mog_present is False:
            data.mog_turn_off_countdown = None
            data.mog_turn_on_countdown = None
            data.mog_stay_off_countdown = None

        if self.sog0_present is False:
            data.sog0_turn_off_countdown = None
            data.sog0_turn_on_countdown = None
            data.sog0_stay_off_countdown = None

        if self.sog1_present is False:
            data.sog1_turn_off_countdown = None
            data.sog1_turn_on_countdown = None
            data.sog1_stay_off_countdown = None

        if self.sog2_present is False:
            data.sog2_turn_off_countdown = None
            data.sog2_turn_on_countdown = None
            data.sog2_stay_off_countdown = None

        if self.sog3_present is False:
            data.sog3_turn_off_countdown = None
            data.sog3_turn_on_countdown = None
            data.sog3_stay_off_countdown = None
        return data

    def _calculate_apparent_power(self, output0_apparent_power_pct: float) -> float:
        return (
            output0_apparent_power_pct
            / 100
            * self.inventory_data.output_apparent_power_rating
        )

    def _calculate_real_power(self, output0_real_power_pct: float) -> float:
        return (
            output0_real_power_pct / 100 * self.inventory_data.output_real_power_rating
        )

    def fetch_settings(self) -> Settings:
        if self.inventory_data is None:
            self.fetch_inventory_data()

        decoder = self._get_data_as_decoder(1024, 50)
        battery_test_interval_setting_bf = decoder.decode_16bit_uint()  # 1024
        decoder.skip_bytes(2)  # 1025
        output_upper_acceptable_voltage_setting = decoder.decode_16bit_uint()  # 1026
        output_lower_acceptable_voltage_setting = decoder.decode_16bit_uint()  # 1027
        output_sensitivity_setting_bf = decoder.decode_16bit_uint()  # 1028
        mog_turn_off_countdown_setting = decoder.decode_16bit_int()  # 1029
        mog_turn_on_countdown_setting = decoder.decode_16bit_int()  # 1030
        mog_stay_off_countdown_setting = decoder.decode_32bit_int()  # 1031
        mog_minimum_return_runtime_setting = decoder.decode_16bit_uint()  # 1033
        sog0_turn_off_countdown_setting = decoder.decode_16bit_int()  # 1034
        sog0_turn_on_countdown_setting = decoder.decode_16bit_int()  # 1035
        sog0_stay_off_countdown_setting = decoder.decode_32bit_int()  # 1036
        sog0_minimum_return_runtime_setting = decoder.decode_16bit_uint()  # 1038
        sog1_turn_off_countdown_setting = decoder.decode_16bit_int()  # 1039
        sog1_turn_on_countdown_setting = decoder.decode_16bit_int()  # 1040
        sog1_stay_off_countdown_setting = decoder.decode_32bit_int()  # 1041
        sog1_minimum_return_runtime_setting = decoder.decode_16bit_uint()  # 1043
        sog2_turn_off_countdown_setting = decoder.decode_16bit_int()  # 1044
        sog2_turn_on_countdown_setting = decoder.decode_16bit_int()  # 1045
        sog2_stay_off_countdown_setting = decoder.decode_32bit_int()  # 1046
        sog2_minimum_return_runtime_setting = decoder.decode_16bit_uint()  # 1048
        sog3_turn_off_countdown_setting = decoder.decode_16bit_int()  # 1049
        sog3_turn_on_countdown_setting = decoder.decode_16bit_int()  # 1050
        sog3_stay_off_countdown_setting = decoder.decode_32bit_int()  # 1051
        sog3_minimum_return_runtime_setting = decoder.decode_16bit_uint()  # 1053

        battery_test_interval_setting = BatteryTestIntervalSetting(
            battery_test_interval_setting_bf
        )

        output_sensitivity_setting = OutputSensitivitySetting(
            output_sensitivity_setting_bf
        )

        self.static_data = Settings(
            output_upper_acceptable_voltage_setting=output_upper_acceptable_voltage_setting,
            output_lower_acceptable_voltage_setting=output_lower_acceptable_voltage_setting,
            mog_turn_off_countdown_setting=mog_turn_off_countdown_setting,
            mog_turn_on_countdown_setting=mog_turn_on_countdown_setting,
            mog_stay_off_countdown_setting=mog_stay_off_countdown_setting,
            mog_minimum_return_runtime_setting=mog_minimum_return_runtime_setting,
            sog0_turn_off_countdown_setting=sog0_turn_off_countdown_setting,
            sog0_turn_on_countdown_setting=sog0_turn_on_countdown_setting,
            sog0_stay_off_countdown_setting=sog0_stay_off_countdown_setting,
            sog0_minimum_return_runtime_setting=sog0_minimum_return_runtime_setting,
            sog1_turn_off_countdown_setting=sog1_turn_off_countdown_setting,
            sog1_turn_on_countdown_setting=sog1_turn_on_countdown_setting,
            sog1_stay_off_countdown_setting=sog1_stay_off_countdown_setting,
            sog1_minimum_return_runtime_setting=sog1_minimum_return_runtime_setting,
            sog2_turn_off_countdown_setting=sog2_turn_off_countdown_setting,
            sog2_turn_on_countdown_setting=sog2_turn_on_countdown_setting,
            sog2_stay_off_countdown_setting=sog2_stay_off_countdown_setting,
            sog2_minimum_return_runtime_setting=sog2_minimum_return_runtime_setting,
            sog3_turn_off_countdown_setting=sog3_turn_off_countdown_setting,
            sog3_turn_on_countdown_setting=sog3_turn_on_countdown_setting,
            sog3_stay_off_countdown_setting=sog3_stay_off_countdown_setting,
            sog3_minimum_return_runtime_setting=sog3_minimum_return_runtime_setting,
            battery_test_interval_setting=battery_test_interval_setting,
            output_sensitivity_setting=output_sensitivity_setting,
        )
        self._set_settings_sogs(self.static_data)
        return self.static_data

    def _set_settings_sogs(self, data: Settings) -> Settings:
        if self.mog_present is False:
            data.mog_turn_off_countdown_setting = None
            data.mog_turn_on_countdown_setting = None
            data.mog_stay_off_countdown_setting = None
            data.mog_minimum_return_runtime_setting = None

        if self.sog0_present is False:
            data.sog0_turn_off_countdown_setting = None
            data.sog0_turn_on_countdown_setting = None
            data.sog0_stay_off_countdown_setting = None
            data.sog0_minimum_return_runtime_setting = None

        if self.sog1_present is False:
            data.sog1_turn_off_countdown_setting = None
            data.sog1_turn_on_countdown_setting = None
            data.sog1_stay_off_countdown_setting = None
            data.sog1_minimum_return_runtime_setting = None

        if self.sog2_present is False:
            data.sog2_turn_off_countdown_setting = None
            data.sog2_turn_on_countdown_setting = None
            data.sog2_stay_off_countdown_setting = None
            data.sog2_minimum_return_runtime_setting = None

        if self.sog3_present is False:
            data.sog3_turn_off_countdown_setting = None
            data.sog3_turn_on_countdown_setting = None
            data.sog3_stay_off_countdown_setting = None
            data.sog3_minimum_return_runtime_setting = None

        return data

    def fetch_commands_data(self) -> CommandsData:
        result = self._fetch_data(1536, 24)
        decoder = BinaryPayloadDecoder.fromRegisters(result, byteorder=Endian.Big)

        ups_command_bf = decoder.decode_32bit_uint()  # 1536
        outlet_command_bf = decoder.decode_32bit_uint()  # 1538
        simple_signaling_command_bf = decoder.decode_16bit_uint()  # 1540
        replace_battery_test_command_bf = decoder.decode_16bit_uint()  # 1541
        run_time_calibration_command_bf = decoder.decode_16bit_uint()  # 1542
        user_interface_command_bf = decoder.decode_16bit_uint()  # 1543

        ups_command = Upsdommand(ups_command_bf)
        outlet_command = OutletCommand(outlet_command_bf)
        simple_signaling_command = SimpleSignalingCommand(simple_signaling_command_bf)
        replace_battery_test_command = ReplaceBatteryTestCommand(
            replace_battery_test_command_bf
        )
        run_time_calibration_command = RuntimeCalibrationCommand(
            run_time_calibration_command_bf
        )
        user_interface_command = UserInterfaceCommand(user_interface_command_bf)

        return CommandsData(
            ups_command=ups_command,
            outlet_command=outlet_command,
            simple_signaling_command=simple_signaling_command,
            replace_battery_test_command=replace_battery_test_command,
            run_time_calibration_command=run_time_calibration_command,
            user_interface_command=user_interface_command,
        )

    def fetch_verification_data(self) -> dict:
        result = self._fetch_data(2048, 28)
        decoder = BinaryPayloadDecoder.fromRegisters(result, byteorder=Endian.Big)

        modbus_map_ID = decoder.decode_string(4)
        test_string = decoder.decode_string(8)  # 12345678
        test_number1 = decoder.decode_32bit_uint()  # 0x12345678 = 305419896
        test_number2 = decoder.decode_32bit_int()  # -5
        test_2b_number1 = decoder.decode_16bit_uint()  # 0x1234 = 4660
        test_2b_number2 = decoder.decode_16bit_int()  # -5
        test_bpin_number1 = decoder.decode_16bit_uint() / 64  # 128.5
        test_bpin_number2 = decoder.decode_16bit_int() / 64  # -128.5

        return VerificationData(
            modbus_map_ID=modbus_map_ID,
            test_string=test_string,
            test_number1=test_number1,
            test_number2=test_number2,
            test_2b_number1=test_2b_number1,
            test_2b_number2=test_2b_number2,
            test_bpin_number1=test_bpin_number1,
            test_bpin_number2=test_bpin_number2,
        )
