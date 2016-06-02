from .. import ivi
from .. import rfsiggen
from .. import scpi 
from ..rfsiggen import TriggerSource
from ..rfsiggen import IQSource
from ..rfsiggen import LFGeneratorWaveform

import os

class rsSettingConflictException(ivi.IviException): pass

class rsBaseSM(scpi.common.IdnCommand, scpi.common.ErrorQuery,
               scpi.common.Reset, scpi.common.SelfTest, scpi.common.Memory,
               rfsiggen.ModulateIQ,
               rfsiggen.Base, rfsiggen.ModulateAM,
               rfsiggen.LFGenerator, rfsiggen.LFGeneratorOutput,
               rfsiggen.IQImpairment, rfsiggen.ArbGenerator,
               ivi.Driver):
    
    "Rohde & Schwarz SM... series IVI RF signal generator driver" 
    
    def __init__(self, *args, **kwargs):
        self.__dict__.setdefault('_instrument_id', '')
        super(rsBaseSM, self).__init__(*args, **kwargs)
        
        self._frequency_low = 250e3
        
        self._frequency_high = 4e9
        self._identity_description = "Rohde & Schwarz SM... serie IVI RF signal generator driver"
        self._identity_identifier = ""
        self._identity_instrument_manufacturer = "Rohde & Schwarz"
        self._identity_revision = ""
        self._identity_vendor = ""
        self._identity_instrument_model = ""
        self._identity_instrument_firmware_revision = ""
        self._identity_specification_major_version = 1
        self._identity_specification_minor_version = 0
        self._identity_supported_instrument_models = list(['SMW200A', 'SMBV100A', 'SMU200A',
                'SMATE200A', 'SMJ100A', 'AMU200A'])
        
        self._add_method('memory.write_from_file_to_instrument',
                        self._write_from_file_to_instrument, 
                        )
        self._add_method('memory.read_to_file_from_instrument',
                        self._read_to_file_from_instrument,
                        )
        self._add_method('memory.delete_file_from_instrument',
                        self._delete_file_from_instrument,
                        )
        
    def _initialize(self, resource=None, id_query=False, reset=False, **keywargs):
        "Opens an I/O session to the instrument."

        super(rsBaseSM, self)._initialize(resource, id_query, reset, **keywargs)

        if self._driver_operation_simulate:
            self._interface = "simulate"  
            
        # interface clear
        self._clear()

        # check ID
        if id_query :
            id = self.identity.instrument_model
            id_check = self._instrument_id
            id_short = id[:len(id_check)]
            if id_short != id_check:
                raise Exception("Instrument ID mismatch, expecting %s, got %s", id_check, id_short)

        # reset
        if reset:
            self._utility_reset()
    
#Base      
    def _get_rf_frequency(self):
        try : 
            self._rf_frequency = float(self._ask(":SOUR:FREQ:CW?"))
        except ValueError: 
            self._rf_frequency = 0.0
        self._set_cache_valid()
        return self._rf_frequency
        
    def _set_rf_frequency(self, value):
        self._write(":SOUR:FREQ:CW %e" % value)
        self._rf_frequency = value
        self._set_cache_valid()   
        
    def _get_rf_level(self):
        try : 
            self._rf_level = float(self._ask(":SOUR:POW:LEV:IMM:AMPL?"))
        except ValueError: 
            self._rf_level = 0.0
        self._set_cache_valid()
        return self._rf_level
    
    def _set_rf_level(self, value):
        self._write(":SOUR:POW:LEV:IMM:AMPL %e" % value)
        self._rf_level = value
        self._set_cache_valid()   
            
    def _get_rf_output_enabled(self):
        try : 
            self._rf_output_enabled = bool(int(self._ask(":OUTP:STATE?")))
        except ValueError: 
            self._rf_output_enabled = 0
        self._set_cache_valid()
        return self._rf_output_enabled

    def _set_rf_output_enabled(self, value):
        value = bool(value)
        self._write(":OUTP:STATE %d" % int(value))
        self._rf_output_enabled = value
        self._set_cache_valid()
        
#LFGenerator
    def _get_lf_generator_frequency(self):
        try : 
            self._lf_generator_frequency = float(self._ask(":SOUR:LFO:FREQ?"))
        except ValueError: 
            self._lf_generator_frequency = 0.0
        self._set_cache_valid()
        return self._lf_generator_frequency
    
    def _set_lf_generator_frequency(self, value):
        value = float(value)
        self._write(":SOUR:LFO:FREQ %e" % value)
        self._lf_generator_frequency = value
        self._set_cache_valid()
        
    def _get_lf_generator_waveform(self):
        try : 
            self._lf_generator_waveform = self._ask(":SOUR:LFO:SHAP?")
        except ValueError: 
            self._lf_generator_waveform = 'sine'
        self._set_cache_valid()     
        return self._lf_generator_waveform
    
    def _set_lf_generator_waveform(self, value):
        if value not in LFGeneratorWaveform:
            raise ivi.ValueNotSupportedException()
        self._write(":SOUR:LFO:SHAP %s" % value)
        self._lf_generator_waveform = value
        self._set_cache_valid()

    def _get_lf_generator_output_amplitude(self):
        try : 
            self._lf_generator_output_amplitude = float(self._ask(":SOUR:LFO:VOLT?"))
        except ValueError: 
            self._lf_generator_output_amplitude = 1.000
        self._set_cache_valid()     
        return self._lf_generator_output_amplitude
    
    def _set_lf_generator_output_amplitude(self, value):
        value = float(value)
        self._write(":SOUR:LFO:VOLT %e" % value)
        self._lf_generator_output_amplitude = value
        self._set_cache_valid()
         
    def _get_lf_generator_output_enabled(self):
        try : 
            self._lf_generator_output_enabled = bool(int(self._ask(":SOUR:LFO:STAT?")))
        except ValueError: 
            self._lf_generator_output_enabled = False
        self._set_cache_valid()     
        return self._lf_generator_output_enabled
    
    def _set_lf_generator_output_enabled(self, value):
        value = bool(value)
        self._write(":SOUR:LFO:STAT %d" %int(value))
        self._lf_generator_output_enabled = value
        self._set_cache_valid()
        
#Modulate IQ 
    def _get_iq_enabled(self):
        try : 
            self._iq_enabled = bool(int(self._ask(":SOUR:IQ:STAT?")))
        except ValueError: 
            self._iq_enabled = 0
        self._set_cache_valid()
        return self._iq_enabled
    
    def _set_iq_enabled(self, value):
        value = bool(value)
        self._write(":SOUR:IQ:STAT %d" % int(value))
        self._iq_enabled = value
        self._set_cache_valid()
    
    def _get_iq_source(self):
        return self._iq_source
    
    def _set_iq_source(self, value):
        if value not in IQSource:
            raise ivi.ValueNotSupportedException()
        self._write(":SOUR:BB:ARB:STAT 0")
        self._write(":SOUR:BB:DM:STAT 0")
        if value == 'external':
            self._write(":SOUR:IQ:SOUR ANAL")
        if value == 'arb_generator':
            self._write(":SOUR:IQ:SOUR BAS")
            self._write(":SOUR:BB:ARB:STAT 1")
        if value == 'digital_modulation_base':
            self._write(":SOUR:IQ:SOUR BAS")
            self._write(":SOUR:BB:DM:STAT 1")
        self._iq_source = value
        self._set_cache_valid()  
              
#ArbGenerator    
    def _get_digital_modulation_arb_selected_waveform(self):
        try : 
            self._digital_modulation_arb_selected_waveform = self._ask(":SOUR:BB:ARB:WAV:SEL?")
        except ValueError: 
            self._digital_modulation_arb_selected_waveform = ""
        self._set_cache_valid()
        return self._digital_modulation_arb_selected_waveform 
    
    def _set_digital_modulation_arb_selected_waveform(self, value):
        value = str(value)
        self._write(":SOUR:BB:ARB:WAV:SEL '%s'" % value)
        self._digital_modulation_arb_selected_waveform = value
        self._set_cache_valid()
    
    def _get_digital_modulation_arb_clock_frequency(self):
        try : 
            self._digital_modulation_arb_clock_frequency = float(self._ask(":SOUR:BB:ARB:WAV:SEL?"))
        except ValueError: 
            self._digital_modulation_arb_clock_frequency = 0.0
        self._set_cache_valid()
        return self._digital_modulation_arb_clock_frequency
    
    def _set_digital_modulation_arb_clock_frequency(self, value):
        value = float(value)
        self._write(":SOUR:BB:ARB:WAV:CLOCK '%e'" % value)
        self._digital_modulation_arb_clock_frequency = value
        self._set_cache_valid()
    
    def _get_digital_modulation_arb_trigger_source(self):
        return self._digital_modulation_arb_trigger_source
    
    def _set_digital_modulation_arb_trigger_source(self, value):
        if value not in TriggerSource:
            raise ivi.ValueNotSupportedException()
        if value == "immediate":
            self._write(":SOUR:BB:ARB:TRIG:SEQ AUTO") 
        if value == "external":
            self._write(":SOUR:BB:ARB:TRIG:SEQ SING")
            self._write(":SOUR:BB:ARB:TRIG:SOUR EXT")
        if value == "software":
            self._write(":SOUR:BB:ARB:TRIG:SEQ SING")
            self._write(":SOUR:BB:ARB:TRIG:SOUR INT")
        self._digital_modulation_arb_trigger_source = value
        self._set_cache_valid()
        
#Custom field
    def _write_from_file_to_instrument(self, source, destination):
        data = open(source, 'rb').read()
        command = ":MMEM:DATA '%s' ,#%s%s" % (destination + 
                                              os.path.basename(source), 
                                              len(str(len(data))), len(data))
        self._write(command)
        self._write_raw(data)
        
    def _read_to_file_from_instrument(self, source, destination):
        raise NotImplementedError()
        
    def _delete_file_from_instrument(self, source):
        self._write(":MMEM:DEL '%s'" % source)   
