** SPICE Deck created by TSMC ADC Timing Team ***
* DONT_TOUCH_PINS
* CELL SDFSRPQSXGMZD4BWP130HPNPN3P48CPD | REL_PIN CP | REL_PIN_DIR rise | CONSTR_PIN SI | CONSTR_PIN_DIR fall | OUTPUT_PINS Q | PROBE_PIN_1 Q | WHEN notCD_D_SDN_SE | OUTPUT_LOAD 0.002199 | TEMPLATE_PINLIST CD CP D SDN SE SI Q | ARC_TYPE hold | VECTOR xRxxxFx
* REL_PIN_SLEWS 0.0019 0.0729 0.2149 0.4988 1.0667 | CONSTR_PIN_SLEWS 0.0019 0.5336 1.5971 3.7240 7.9962 | MAX_SLEW 7.9962
* TEMPLATE_DECK hold/template__common__rise__fall__1.sp


* THANOS Headers
* CONSTR_CRITERIA | pushout
* OPT_RESULTS | cp2q_del1 cp2q_del2
* MEAS_DEGRADE_PER cp2q_del1 | 0.4
* MEAS_DEGRADE_PER cp2q_del2 |
* CONSTR_PIN_PARAM | constrained_pin_t02

* SPICE options
.options runlvl=6 ACCURATE=1 BRIEF=1 MODSRH=1 gmindc=1e-15 gdcpath=1e-15 method=gear converge=100 pode_check=0 autostop post=0 NOMOD=1 MEASDGT=7 measform=1 measfile=1 statfl=1 MCBRIEF=5 sampling_method=lhs
.save level=none

* Waveform
.inc '/CAD/stdcell/DesignKits/Sponsor/Script/MCQC_automation/Template/std_wv_c651.spi'

* Model include file
.inc '/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2025/N2P_v1.0/1-MC_golden/0-FMC_golden/gen_DECKs/ssgnp_0p450v_m40c_DECKS/hold/ssgnp_0p450v_m40c_cworst_CCworst_T.hold.inc'

* Netlist path
.inc '/SIM/DFDS_20211231/Personal/ynie/3-LibCharCerti/2025/N2P_v1.0/1-MC_golden/0-FMC_golden/Collaterals/kits/base/3svt/Netlist/LPE_cworst_CCworst_T_m40c/SDFSRPQSXGMZD4BWP130HPNPN3P48CPD.spi'

* Library information
.param vdd_value = '0.450'
.param vss_value = 0
.temp -40

* Slew and load information
.param cl = '0.002199p'
.param rel_pin_slew = '0.4988n'
.param constr_pin_slew = '0.5336n'

* Voltage
VVDD VDD 0 'vdd_value'
VVSS VSS 0 'vss_value'
VVPP VPP 0 'vdd_value'
VVBB VBB 0 'vss_value'

* Output Load
CQ Q 0 'cl'

* Subckt Definition
X1 SI D SE CP CD SDN Q VDD VSS VPP VBB SDFSRPQSXGMZD4BWP130HPNPN3P48CPD

* Waveform timestamps
.param max_slew = '7.9962n'
.param constrained_pin_t01 = '5 * max_slew'
.param constrained_pin_t02 = '20 * max_slew'
.param related_pin_t01 = '0.0n'
.param related_pin_t02 = '10 * max_slew'
.param related_pin_t03 = '20 * max_slew'
.param related_pin_t04 = '30 * max_slew'
.param related_pin_t05 = '40 * max_slew'

* Optimization settings
.param opt_init = '20 * max_slew'
.param opt_ub = '25 * max_slew'
.param opt_lb = '15 * max_slew'
*.param constr_pin_offset = OPT1('opt_init', 'opt_lb', 'opt_ub')
* [1ps tolerance] relin = 0.001 / (opt_ub - opt_lb)
*.MODEL optmod opt METHOD=passfail itropt=100 relin='1ps / (opt_ub - opt_lb)'

* Pin definitions
VCD CD 0 'vss_value'
VD D 0 'vdd_value'
VSDN SDN 0 'vdd_value'
VSE SE 0 'vdd_value'

* Unspecified pins


* Toggling pins
XVCP CP 0 stdvs_rise_fall_rise_fall_rise VDD='vdd_value' slew='rel_pin_slew' t01='related_pin_t01' t02='related_pin_t02' t03='related_pin_t03' t04='related_pin_t04' t05='related_pin_t05'
XVSI SI 0 stdvs_rise_fall VDD='vdd_value' slew='constr_pin_slew' t01='constrained_pin_t01' t02='constrained_pin_t02'

* Measurements
.meas cp2q_del1 trig v(CP) val='vdd_value/2' cross=3 targ v(Q)  td='related_pin_t03' val='vdd_value/2' cross=1
.meas cp2q_del2 trig v(CP) val='vdd_value/2' cross=5 targ v(Q)  td='related_pin_t05' val='vdd_value/2' cross=1
.meas cp2d trig v(CP) val='vdd_value/2' cross=3 targ v(SI) val='vdd_value/2' cross=2

* Transient Sim Command
.tran 1p 5000n sweep monte=1 monte=1

.end
