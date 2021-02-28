/**3D SCANNER** * DATED : 020121
 * DEVELOPER : ARV
 * COMPONENTS : IR Sharp Distance Sensor, Stepper Motor (5V), DC Motor, L293D Driver, Python Script (GUI Window App)
 */
/*PINOUT MAP
 * COMPONENT            ARDUINO
 * L293D IN0            D2
 * L293D IN1            D3
 * STEPPER COIL1        D8 
 * STEPPER COIL2        D9 
 * STEPPER COIL3        D10 
 * STEPPER COIL4        D11 
 * IR SHARP             A1
 */
 
//MACROS
//#define DEBUG 1
#define COIL1 8 
#define COIL2 9 
#define COIL3 10 
#define COIL4 11
#define IN0 6 
#define IN1 7 
#define IR A1
#define SP1 digitalWrite(COIL1,HIGH);digitalWrite(COIL2,LOW);digitalWrite(COIL3,LOW);digitalWrite(COIL4,LOW)
#define SP2 digitalWrite(COIL1,HIGH);digitalWrite(COIL2,HIGH);digitalWrite(COIL3,LOW);digitalWrite(COIL4,LOW)
#define SP3 digitalWrite(COIL1,LOW);digitalWrite(COIL2,HIGH);digitalWrite(COIL3,LOW);digitalWrite(COIL4,LOW)
#define SP4 digitalWrite(COIL1,LOW);digitalWrite(COIL2,HIGH);digitalWrite(COIL3,HIGH);digitalWrite(COIL4,LOW)
#define SP5 digitalWrite(COIL1,LOW);digitalWrite(COIL2,LOW);digitalWrite(COIL3,HIGH);digitalWrite(COIL4,LOW)
#define SP6 digitalWrite(COIL1,LOW);digitalWrite(COIL2,LOW);digitalWrite(COIL3,HIGH);digitalWrite(COIL4,HIGH)
#define SP7 digitalWrite(COIL1,LOW);digitalWrite(COIL2,LOW);digitalWrite(COIL3,LOW);digitalWrite(COIL4,HIGH)
#define SP8 digitalWrite(COIL1,HIGH);digitalWrite(COIL2,LOW);digitalWrite(COIL3,LOW);digitalWrite(COIL4,HIGH)
#define SPRST digitalWrite(COIL1,LOW);digitalWrite(COIL2,LOW);digitalWrite(COIL3,LOW);digitalWrite(COIL4,LOW)
#define MOTOR_CW digitalWrite(IN0,HIGH);digitalWrite(IN1,LOW)
#define MOTOR_ACW digitalWrite(IN0,LOW);digitalWrite(IN1,HIGH)
#define MOTOR_STOP digitalWrite(IN0,LOW);digitalWrite(IN1,LOW)
#define STEP_DELAY 2.5
#define ANGLE 8 //5.625 degrees steps 64:1
#define MOTOR_DELAY 15000 //15 sec =2.5mm elevation
#define READ_SAMPLE 100
#define READ_DELAY 250
#define k1 16.7647563
#define k2 -0.85803107
#define CW 0
#define ACW 1
#define RUN_CW 2
#define RUN_ACW 3
#define STOP 4
#define RESET 5

#define RIGHT 0
#define LEFT 1
#define THRESHOLD 14
//VARIABLES 
float ADC_sum,ADC_volt,distance,cnt=13.5;
char ch,tmp;
uint8_t z_ctr;
//FP
void stepper_cw(boolean);
void motor(uint8_t);
void compute_dist();
void scan();
void compute(boolean);
//INIT
void setup() 
{
 //STEPPER CONFIG
  pinMode(COIL1,OUTPUT);pinMode(COIL2,OUTPUT);
  pinMode(COIL3,OUTPUT);pinMode(COIL4,OUTPUT);
  pinMode(13,OUTPUT);
  SPRST;
 //MOTOR CONFIG
 pinMode(IN0,OUTPUT);pinMode(IN1,OUTPUT);
 MOTOR_STOP;
 //SERIAL
 Serial.begin(9600);
 #ifdef DEBUG
 Serial.println("-----READY---------");
 #endif
 //ANALOG REFERENCE
 //analogReference(EXTERNAL);
}
//FUNCTION DEFINED
void stepper_cw(boolean dir)
{
  if(dir)
  {for(uint8_t i=0;i<ANGLE;i++)
  {
    SP8;delay(STEP_DELAY);
    SP7;delay(STEP_DELAY);
    SP6;delay(STEP_DELAY);
    SP5;delay(STEP_DELAY);
    SP4;delay(STEP_DELAY);
    SP3;delay(STEP_DELAY);
    SP2;delay(STEP_DELAY);
    SP1;delay(STEP_DELAY);
  }}
  else
  {for(uint8_t i=0;i<ANGLE;i++)
  {
    SP1;delay(STEP_DELAY);
    SP2;delay(STEP_DELAY);
    SP3;delay(STEP_DELAY);
    SP4;delay(STEP_DELAY);
    SP5;delay(STEP_DELAY);
    SP6;delay(STEP_DELAY);
    SP7;delay(STEP_DELAY);
    SP8;delay(STEP_DELAY);
  }}
  SPRST;
}
void motor(uint8_t m)
{
  if(m==0)
  {
    MOTOR_CW;delay(MOTOR_DELAY);MOTOR_STOP;
  }
  else if(m==1)
  {
    MOTOR_ACW;delay(MOTOR_DELAY);MOTOR_STOP;
  }
  else if(m==2)
  {
    MOTOR_CW;
  }
  else if(m==3)
  {
    MOTOR_ACW;
  }
  else if(m==4)
  {
    MOTOR_STOP;
  }
  else if(m==5)
  {
    MOTOR_ACW;
    for(;z_ctr>0;z_ctr--){ch=Serial.read();delay(MOTOR_DELAY);if(ch=='t')break;}
    MOTOR_STOP;
  }
}
void compute_dist()
{
  delay(READ_DELAY);
  ADC_sum=0;distance=0;
  for (int i=0; i<READ_SAMPLE; i++)
  {
    ADC_sum=ADC_sum+float(analogRead(IR));  
  }
  
  ADC_volt=(ADC_sum/READ_SAMPLE)*5/1024;
  distance = pow(ADC_volt*(1/k1), 1/k2);
//  Serial.println("--------------------");
//  Serial.print(distance);Serial.println(" cm");
//  Serial.println("--------------------");
}
void compute(boolean pt)
{
  delay(READ_DELAY);
  ADC_sum=0;
  for (int i=0; i<READ_SAMPLE; i++)
  {
    ADC_sum=ADC_sum+float(analogRead(IR));
    //delay(5); 
  }
  
  ADC_volt=(ADC_sum/READ_SAMPLE)*5/1024;
  distance = pow(ADC_volt*(1/k1), 1/k2);
  if(pt==1)Serial.println(cnt-distance);
  else if(pt==0){Serial.print(distance);Serial.print(":");Serial.println(cnt);}
}
void scan()
{
  #ifdef DEBUG
  Serial.println("--------------SCANNER STARTED----------------------");
  Serial.println("\t ANGLE \t DISTANCE");
  #endif
  while(1)
  {
    for(uint16_t ctr=0;ctr<64;ctr++)
    {
      #ifdef DEBUG
      Serial.print("\t ");Serial.print(ctr*5.6);Serial.print(" \t");
      #endif
      stepper_cw(LEFT);
      compute(1);
      #ifdef DEBUG
      Serial.println();
      #endif
    }
    motor(CW);
    z_ctr++;
    distance=0;
    compute_dist();
    if(distance<cnt)compute_dist();
    while(!(Serial.available()));
    while(Serial.available())tmp=Serial.read();
    if(distance>=cnt||tmp=='t')
    {distance+=100;Serial.println(distance);break;}
  }
  motor(RESET);z_ctr=0;
  #ifdef DEBUG
  Serial.println("----------------SCANNER STOP----------------------------");
  #endif
}
void loop() 
{
  while(!(Serial.available()));
  ch=Serial.read();
  if(ch=='s')
  stepper_cw(RIGHT);
  if(ch=='r')
  stepper_cw(LEFT);
  else if(ch=='m')
  motor(CW);
  else if(ch=='n')
  motor(ACW);
  else if(ch=='u')
  motor(RUN_CW);
  else if(ch=='l')
  motor(RUN_ACW);
  else if(ch=='p')
  motor(STOP);
  else if(ch=='d')
  compute(0);
  else if(ch=='q')
  scan();
  else if(ch=='S')
  {
    Serial.println("SET");
    while(!(Serial.available()));
    cnt=Serial.read();
    cnt=cnt/10;
  }
  else if(ch=='C')
  Serial.println("READY");
  ch='z';
}
