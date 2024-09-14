
from sympy import * 
from math import sqrt




pi = 3.1415926


print("###########输入电容计算#############")
Vo = 12 #输出电压
Io_max = 4 #最大输出电流
eff = 0.85 #电源效率
Fi_AC = 50#输入交流电频率
Vi_AC_RMS_Min = 176 #交流输入电压范围+- 20%
Vi_AC_RMS_Max = 264
Vbus_pp = 25 #母线电压纹波



Vbus_pk_Min = Vi_AC_RMS_Min * sqrt(2)#母线电压峰值
Tc = 1/(4*Fi_AC) - asin((Vbus_pk_Min-Vbus_pp)/(Vbus_pk_Min))/(2*pi*Fi_AC)#电容充电时间
print("Tc = ",Tc*10**3,"ms")
Td = 1/Fi_AC/2 - Tc
print("Td = ",Td*10**3,"ms")
#母线电容
Pmax = Vo * Io_max / eff #最大功率
print("Pmax = ",Pmax,"W")
Cbus = 2*Pmax*(1/(2*Fi_AC) - Tc)/(eff*(Vbus_pk_Min**2 - (Vbus_pk_Min-Vbus_pp)**2))
print("Cbus = ",Cbus*10**6,"uF")
print("##################################\n")
####################################
#整流桥计算
PF = 0.6 #功率因数
Ii_RMS_Max = Pmax/(eff * Vi_AC_RMS_Min * PF)#交流输入电流


####################################
print("###########耐压匝比计算############")
mos_VDS_max = 600 #mos耐压600V
k_vds = 0.9#降额系数
VRCD_k = 1.3 #RCD波峰电压与反射电压比值
VAUX = 12 #辅助绕组偏置电压

Vbus_pk_Max = Vi_AC_RMS_Max * sqrt(2)
print("Vbus_pk_Max = ",Vbus_pk_Max,"V")
mos_VDS = mos_VDS_max*k_vds
print("mos应力余量=",mos_VDS_max-mos_VDS,"v")
VRCD_pk = mos_VDS - Vbus_pk_Max#RCD波峰电压
print("RCD波峰电压=",VRCD_pk,"V")
VOR = VRCD_pk/VRCD_k#反射电压
print("反射电压=",VOR,"V")
Nps = VOR/(Vo+0.7)#匝比
print("源副边匝比=",Nps)
Nps = int(Nps)
print("源副边匝比取整=",Nps)
Npa = int(Nps * (Vo/VAUX))
print("源辅边匝比=",Npa)
print("####################################\n")

#计算电流
print("###########占空比计算校验############")
Dmax_set = 0.5
VF = 0.7 #输出二极管压降
Dmax = Nps*(Vo+VF)/(Vbus_pk_Min + Nps*(Vo+VF))#依据能量守恒
if Dmax>Dmax_set:
    print("占空比过大，请减小匝比")
print("最大占空比=",Dmax)
print("################################\n")

print("###########原边感量计算############")
Krp = 0.7 #纹波电流与电流峰值的比值，CCM时小于1
Fsw = 95*10**3 #开关频率
Ii_pk = 2*Pmax / ((2-Krp)*Dmax*Vbus_pk_Min)
print("峰值电流=",Ii_pk,"A")
Ii_pp = Ii_pk * Krp #
print("纹波电流=",Ii_pp,"A")

print("################################\n")


print("###########RCD吸收计算校验############")
Ld = 10 * 10**-6 #漏感

print("RCD波峰电压",VRCD_pk,"V")
print("RCD波谷电压",VRCD_pb,"V")

VRCD_Diod = VOR + Vbus_pk_Max
print("RCD二极管应力=",VRCD_Diod,"V")

ELd = 1/2 * Ld * Ii_pk**2#漏感能量
VRCD_RMS = (VRCD_pk + VRCD_pb)/2 #估算，不准
RCD_R  = VRCD_RMS**2 / (ELd*Fsw)

RCD_C = ELd/(1/2 * ((VRCD_pk**2) - (VRCD_pb**2)))
print("RCD吸收电路电阻=",RCD_R*10**-3,"k")
RCD_PR = ELd*Fsw
print("RCD吸收电路电阻功率=",RCD_PR,"W")
print("RCD吸收电路电容=",RCD_C*10**9,"nF")

chr = input("是否重选电阻(y/n)")
#重选吸收电阻
def RCD_rechose():
    RCD_R = 100*10**3
    print("1重选RCD吸收电路电阻=",RCD_R*10**-3,"k")
    RCD_C = 2.2 * 10**-9
    print("1重选RCD吸收电路电容=",RCD_C*10**9,"nF")
    VRCD_RMS = sqrt(ELd * RCD_R * Fsw)
    if(VRCD_RMS <= VOR):
        VRCD_RMS = VOR
        VRCD_pb = VRCD_RMS
        VRCD_pk = sqrt(ELd*2 / RCD_C + VRCD_pb**2)
        print("2重选后RCD波谷电压=",VRCD_pb,"V")
        print("2波峰电压=",VRCD_pk,"V")
        RCD_PR = ELd*Fsw + VOR**2 / RCD_R
        print("RCD吸收电路电阻功率=",RCD_PR,"W")

    else:
        VRCD_pk = sqrt(ELd*2 / RCD_C + VOR**2)
        if(VRCD_pk - VRCD_RMS)>(VRCD_RMS - VOR):
            VRCD_pb = VOR
            print("3重选后RCD波谷电压=",VRCD_pb,"V")
            print("3波峰电压=",VRCD_pk,"V")
            RCD_PR = ELd*Fsw + VOR**2 / RCD_R
            print("RCD吸收电路电阻功率=",RCD_PR,"W")
        else:
           VRCD_pb = VRCD_RMS - ELd/(2*VRCD_RMS*RCD_C)
           print("4重选后RCD波谷电压=",VRCD_pb,"V")
           VRCD_pk = VRCD_RMS + ELd/(2*VRCD_RMS*RCD_C)
           print("4波峰电压=",VRCD_pk,"V")    
           RCD_PR = ELd*Fsw 
           print("RCD吸收电路电阻功率=",RCD_PR,"W") 
                
if(chr == 'y'):
    RCD_rechose()

print("################################\n")



####################################
#变压器感量计算
#Lp = Vbus_AVG_Min*Dmax / (Fsw*Ipp) 
#print("计算得初级线圈电感量=",Lp * 10**3 ,"mH")


#输出电容计算
Vo_pp = 50 * 10**-3

Co = Io_max/(Vo_pp*Fsw)#估算
print("估算输出电容=",Co*10**6,"uF")


Z = 0.5#Z是副边损耗与总损耗的比例值。如果没有更好的参数信息，应当取Z=0.5。
#Lp = Pmax /(Ii_pk**2 * Krp*(1-Krp/2)*Fsw) * ((Z*(1-eff)+eff)/eff)
Lp = Vbus_pk_Max*Dmax/(Fsw * Ipp)
print("初级线圈电感量=",Lp*10**6 ,"uH")

####################################
#磁芯估测选型
Sj = 0.15 * sqrt(Pmax) 
print("磁芯截面积估算为",Sj,"cm2","=",Sj*10**2,"mm2")


#AP法选磁芯，Ap = Aw*Ae
Kw = 0.35 #窗口利用率
J = 400 #电流密度A/cm2
Bmax = 0.3 #磁饱和
AP = 0.433*(1+eff)*Pmax/(eff*Kw*Dmax*J*Bmax*Krp*Fsw)*10**4
print("磁芯AP为",AP,"cm4")


#后面的要查表并实测磁芯后才可以继续
input("后面的要查表并实测磁芯后才可以继续")

Ae = 0.83 * 10**-4 #磁芯截面积
u0 = 1.26 * 10**-6 #空气磁导率
#实测磁芯
class mesuredMagCore :
    N1 = 20
    L1 = 1570 * 10**-6 #在20匝时的电感量
    #N2 = 63
    #L2 = 778 * 10**-6 #磨气隙后在63匝时的电感量 
#磁饱和校验
def oth_calc_Bmax():
    Bmax = Lp*Ii_pk/(Np*Ae)
    print("最大磁感应强度Bmax=",Bmax,"T")

#计算气隙
def oth_calc_lg():
    AL = mesuredMagCore.L1*10**9/mesuredMagCore.N1**2#单位nH/N2
    lg = 40*pi*Ae*10**4*(Np**2/(1000*Lp*10**6) - 1/AL)
    print("气隙长度=",lg,"mm")
#oth_calc_lg()

#计算初级线圈匝数
Np = Lp*Ii_pk / (Bmax*Ae)
print("初级线圈匝数=",Np)
#Ns = Np / Nps_
#print("次级线圈匝数=",Ns)

#重定匝数
def npsReChose():
    Np = 92
    Ns = 17
    lg = 0.4




#####END###############################

#气隙计算
lg = (u0*Ae)*(Np**2 / Lp - mesuredMagCore.N1**2 / mesuredMagCore.L1)#气隙计算公式
print("气隙长度=",lg*10**3,"mm")
#oth_calc_lg()
wire_od = [0.1,0.15,0.2,0.25]




#oth_calc_Bmax()
#calc_Bmax_noGap()
#flybackTransformer_calc()
#testSympy()