// global varialbe dataSet
	var loadingIcon='<i class="loading fa fa-circle-o-notch fa-spin"></i>';
	var entireFile='', entireFile2='';
	var data={};
	var idx = 0; //index for di and da array
	var csv_head=['timestamp','rtua','tnm','battery_volt','battery_charge_curr','battery_charge_power','battery_charge_time','battery_power','single_battery_volt','single_battery_power','battery_temp','dc_charger_output_volt','dc_charger_output_curr','dc_charger_temp','efficiency','charge_qty','charge_amount','status','soc','forward_power','phase_a_volt','phase_b_volt','phase_c_volt','phase_a_curr','phase_b_curr','phase_c_curr','battery_prt_date','max_volt','max_curr','max_temp','battery_soc','max_single_volt','max_single_batt_no','battery_group_no','battery_type','overall_capacity','overall_volt','alr'];
	var csv_cn_head = ['时间戳','终端逻辑地址','测量点','c880-蓄电池组电压','c881-蓄电池组充电电流','c882-蓄电池组充电功率','c883-蓄电池组充电时间','c884-蓄电池组充电电能','c885-单体蓄电池电压','c886-单体蓄电池荷电','c887-蓄电池温度','c888-直流充电机直流输出电压','c889-直流充电机直流输出电流','c88a-直流充电机温度','c88b-转换效率','c88d-所充电量','c88e-消费金额','c840-充电桩状态','c904-电池组SOC','901f-正向有功电能数据块','b611-A相电压','b612-C相电压','b613-C相电压','b621-A相电流','b622-B相电流','b623-C相电流','c900-电池组生产日期','c901-最大允许充电电压','c902-最大允许充电电流','c903-最大允许充电温度','c904-电池组SOC','c905-最高单体电压','c906-最高单体电压电池编号','c907-电池组序号','c908-电池类型','c909-整车动力蓄电池系统额定容量','c90a-整车动力蓄电池系统额定电压','告警'];

//--------------------------------
//code | length | description
//68 H | 1 | Start byte
//RTUA | 4 | Remote terminal address
//MSTA | 2 | Master station address
//68 H | 1 | start byte
//C    | 1 | control code
//L    | 2 | length
//tnm  | 8 | tnm
//Data | ? | Data
//CS   | 1 | Checksum
//16H  | 1 | Ending code
//----------------------------------
function hexDecode(){
	console.log('HEX decode clicked');
	$('#hexDecode').append(loadingIcon); //add loading icon
	setTimeout(function(){ //to let the loading icon show up
		//var entireFile2 = document.getElementById('hex-content').value;
		var lines = entireFile2.split('\n');
		//$('#csv-content').val(csv_head.toString()+'\n'); //add csv header ****
		console.log("lines:",lines.length);
		for(var line = 0; line < lines.length; line++){
			data={};
			data.di=[]; data.da=[];
			idx=0;
			lineArr = lines[line].split('-'); //put line to line array, remove '-'
			//console.log('linearr:',lineArr);
			if (lineArr.length<=1) continue;
			//console.log("line array:",lineArr.length);
			var str="";
			data.timestamp = lineArr.shift(); //get the timestamp
			lineArr.shift(); //skip first 68H
			data.rtua = lineArr.splice(0,4).join(''); //get remote terminal address
			data.msta = lineArr.splice(0,2).join(''); //get master station address
			lineArr.shift(); //skip 2nd 68H
			var control_code = lineArr.shift(); //get control code
			//console.log('control_code:',control_code);
			var hexLength1 = lineArr.shift(); //LSB of length
			var hexLength2 = lineArr.shift(); //MSB of length
			data.len = parseInt(hexLength1, 16) + (parseInt(hexLength2, 16) * 256);
			
			switch (control_code) {
			case '01':
				data.di=[];
				data.direction=0;
				data.action="read current status";
				data.tnm = lineArr.splice(0,8).join(''); //get TNM
				var len = data.length-8;
				//console.log('len:',len);
				for (var i=0; i<len/2; i++) {
					temp1 = lineArr.shift();
					temp2 = lineArr.shift();
					data.di[i] = ''+temp2+temp1;
				}
				break;
			case '02':
				data.direction=0;
				data.action="read task status";
				break;
			case '03':
				data.direction=0;
				data.action="read charge record";
				break;
			case '04':
				data.direction=0;
				data.action="read program log";
				break;
			case '07':
				data.direction=0;
				data.action="write realtime object param";
				break;
			case '08':
				data.direction=0;
				data.action="read object param";
			break;
			case '09':
				data.direction=0;
				data.action="response abnormal alert";
				break;
			case '0a':
				data.direction=0;
				data.action="alert confirm";
				break;
			case '0b':
				data.direction=0;
				data.action="upload charge record confirm";
				break;
			case '0e':
				data.direction=0;
				data.action="backend control charge stop";
				break;
			case '0f':
				data.direction=0;
				data.action="remote upgrade command";
				break;
			
			case '81':
				data.direction = 1;
				data.action="response current status"
				//data.tnm = lineArr.splice(0,8).join(''); //get TNM
				data.di[0]='timestamp';
				data.da[0]=data.timestamp;
				data.di[1]='rtua'; //put remote terminal address to the array
				data.da[1]=data.rtua;
				//------get the tnm; 1->0, 2->1, 4->2, 8->3
				var value = lineArr.splice(0,1); //get TNM
				var i=0;
				for (i=0; i<8; i++){
					if (value == 1<<i) break;
				}
				//console.log('i:',i);
				data.di[2]='tnm';
				data.da[2]= i; //0,1,2,3....
				lineArr.splice(0,7); //trash another 7 bytes from TNM
				
				idx=3;
				//var len = data.len-8;
				do {
					temp1 = lineArr.shift();
					temp2 = lineArr.shift();
					command = ''+temp2+temp1;
					//console.log('command:',command);
					lineArr = testDataDecode(command,lineArr);
					//console.log('lineArr len:',lineArr.length);
				} while (lineArr.length>2);
				break;
			case '82':
				data.direction=1;
				data.action="response task status";
				break;
			case '83':
				idx=0;
				data.direction=1;
				data.action="response charge record";
				lineArr.splice(0,3); //trash 3 x 0
				/*68-10-01-58-42-00-00-68-83-87-00-00-00- 01- 
				00- 15-21-71-24-00- 00-00-00- 66-10-31-03-17-20-00-15- 66-10-31-03-17-20-00-15- 01-00- 01-00-
				95-23-62-15- 00-00-00-00- 50-92-15-00- 65-89-31-15- 80-41-14-00-
				95-23-62-15- 00-00-00-00- 50-92-15-00- 65-89-31-15- 80-41-14-00-
				00-35-01- 00-35-01- 00-35-01- 00-35-01- 00-00-00- 35-28-00-13-10-17- 35-28-00-13-10-17- 
				00-00-00- 47-10-26-08- 00-00-00-00- 
				00-00-00-00-00- 00-58-42-01-10- 00-00-00-00-00- 00-00-00-00-00- 01- 
				00-00-00- 03- d7-16
				
				chg_type=0, pile_seq_id=0024712115, area_code=000000, card_no1=1500201703311066, card_no2=1500201703311066, card_type1=0001, card_type2=0001,
				pre_zxygz=156223.95, pre_zxygz1=0.0, pre_zxygz2=1592.5, pre_zxygz3=153189.65, pre_zxygz4=1441.8, 
				cur_zxygz=156223.95, cur_zxygz1=0.0, cur_zxygz2=1592.5, cur_zxygz3=153189.65, cur_zxygz4=1441.8, 
				prc_zxygz1=1.35, prc_zxygz2=1.35, prc_zxygz3=1.35, prc_zxygz4=1.35, prc_park=0.0, sta_time=2017-10-13 0:28:35, end_time=2017-10-13 00:28:35, 
				park_fee=0.0, pre_amount=82610.47, ?
				card_count=0000000000, trmAddr=1001425800, card_version=0000000000, pos_number=0000000000, card_state_code=1, 
				type=0, gun_no=3, 
				
				portNo=3, cardNo=1500201703311066,   
				cur_amount=0.0, pile_no=1001425800, status=1, */
				data.di=['chg_type','pile_seq_id','area_code','card_no1','card_no2','card_type1','card_type2','pre_zxygz',
				'pre_zxygz1','pre_zxygz2','pre_zxygz3','pre_zxygz4','cur_zxygz','cur_zxygz1','cur_zxygz2','cur_zxygz3','cur_zxygz4',
				'prc_zxygz1','prc_zxygz2','prc_zxygz3','prc_zxygz4','prc_park','sta_time','end_time','park_fee','pre_amount',
				'post_amount','card_count','trmaddr','card_version','pos_number','card_state_code','card_state_code','type','gun_no'];
				lineArr = chargeRecordDecode(lineArr,1,0); //chg_type,交易类型
				lineArr = chargeRecordDecode(lineArr,5,0); //pile_seq_id,交易流水号
				lineArr = chargeRecordDecode(lineArr,3,0); //area_code,地区代码
				lineArr = chargeRecordDecode(lineArr,8,0); //card_no1,开始卡号
				lineArr = chargeRecordDecode(lineArr,8,0); //card_no2,结束卡号
				lineArr = chargeRecordDecode(lineArr,2,0); //card_type1,开始卡型
				lineArr = chargeRecordDecode(lineArr,2,0); //card_type2,结束卡型
				lineArr = chargeRecordDecode(lineArr,4,100); //pre_zxygz,开始交易电量行度（单位：度）
				lineArr = chargeRecordDecode(lineArr,4,100); //pre_zxygz1,开始交易费率1电量行度（单位：度）
				lineArr = chargeRecordDecode(lineArr,4,100); //pre_zxygz2,开始交易费率2电量行度（单位：度）
				lineArr = chargeRecordDecode(lineArr,4,100); //pre_zxygz3,开始交易费率3电量行度（单位：度）
				lineArr = chargeRecordDecode(lineArr,4,100); //pre_zxygz4,开始交易费率4电量行度（单位：度）
				lineArr = chargeRecordDecode(lineArr,4,100); //cur_zxygz,当前交易电量行度（单位：度）
				lineArr = chargeRecordDecode(lineArr,4,100); //cur_zxygz1,当前交易费率1电量行度（单位：度）
				lineArr = chargeRecordDecode(lineArr,4,100); //cur_zxygz2,当前交易费率2电量行度（单位：度）
				lineArr = chargeRecordDecode(lineArr,4,100); //cur_zxygz3,当前交易费率3电量行度（单位：度）
				lineArr = chargeRecordDecode(lineArr,4,100); //cur_zxygz4,当前交易费率4电量行度（单位：度）
				lineArr = chargeRecordDecode(lineArr,3,10000); //prc_zxygz1,结束交易费率1电量行度（单位：度）
				lineArr = chargeRecordDecode(lineArr,3,10000); //prc_zxygz2,结束交易费率2电量行度（单位：度）
				lineArr = chargeRecordDecode(lineArr,3,10000); //prc_zxygz3,结束交易费率3电量行度（单位：度）
				lineArr = chargeRecordDecode(lineArr,3,10000); //prc_zxygz4,结束交易费率4电量行度（单位：度）
				lineArr = chargeRecordDecode(lineArr,3,10000); //prc_park,停车费单价(单位：元/小时)
				lineArr = chargeRecordDecode(lineArr,6,0); //sta_time,交易开始日期、时间
				lineArr = chargeRecordDecode(lineArr,6,0); //end_time,交易结束日期、时间
				lineArr = chargeRecordDecode(lineArr,3,100); //park_fee,停车费 （单位：元）
				lineArr = chargeRecordDecode(lineArr,4,100); //pre_amount,交易前余额 （单位：元）
				lineArr = chargeRecordDecode(lineArr,4,100); //post_amount,交易后余额 （单位：元）
				lineArr = chargeRecordDecode(lineArr,5,0); //card_count,卡交易计数器
				lineArr = chargeRecordDecode(lineArr,5,0); //trmaddr,终端号
				lineArr = chargeRecordDecode(lineArr,5,0); //card_version,卡版本号
				lineArr = chargeRecordDecode(lineArr,5,0); //pos_number,POS机号
				lineArr = chargeRecordDecode(lineArr,1,0); //card_state_code,卡状态码
				lineArr = chargeRecordDecode(lineArr,3,0); //type,车辆识别码（VIN）
				lineArr = chargeRecordDecode(lineArr,1,0); //gun_no,枪号
				break;
			case '84':
				data.direction=1;
				data.action="response program log";
				break;
			case '87':
				data.direction=0;
				data.action="response realtime object param";
				break;
			case '88':
				data.direction=1;
				data.action="response object param";
				break;
			case '89':
				data.direction=1;
				data.action="abnormal alert";
				data.di[0]='timestamp';
				data.da[0]=data.timestamp;
				data.di[1]='rtua'; //put remote terminal address to the array
				data.da[1]=data.rtua;
				var alrn = lineArr.splice(0,1); //get alrn, normally alrn=1
				lineArr.splice(0,1); //skip TN
				lineArr.splice(0,5); //skip alarm time, YY/MM/DD/HH/MM
				var temp=[];
				for (var i = 0; i<2; i++){
					temp.unshift(lineArr.shift());  //get the alarm code. LSB first
				}
				var count = temp.join('');
				data.di[2]='alr'; //alarm code, 01xx
				data.da[2]= count;
				//console.log('data:',JSON.stringify(data));
				break;
			case '8a':
				data.direction=1;
				data.action="response alert confirm";
				break;
			case '8b':
				data.direction=0;
				data.action="response upload charge record confirm";
				break;
			case '8e':
				data.direction=1;
				data.action="response backend control charge stop";
				break;
			case '8f':
				data.direction=1;
				data.action="response remote upgrade command";
				break;
			default:
				break;
			}
			if (data.direction == 0) continue; //if read command, skip
			if (!(control_code == 81 || control_code == 89)) continue;
			//str = JSON.stringify(data)+'\n';
			var csv_arr=[]; //arr to hold csv output
			for (var i=0; i<csv_head.length; i++){ // match the DI/DA in csv_head, store to csv_arr
				var ii = data.di.indexOf(csv_head[i]);
				if (ii != -1) { //find the variable name in csv_head
					csv_arr[i]=data.da[ii];
				} else {
					csv_arr[i]='';
				}
			}
			//console.log('csv_arr:',csv_arr);
			var str = '\"['+csv_arr.join()+']\"'+'\n';
			csvcontent = $('#csv-content');
			$('#csv-content').val(csvcontent.val()+str); //append to text area and add linefeed
		}	//for loop
		//console.log("line:",line);
		$('.loading').remove(); //remove loading icon
	},10);
}

function chargeRecordDecode(lineArr,digit,divisor){
	var temp=[];
	for (var i = 0; i<digit; i++){
		temp.unshift(lineArr.shift()); 
	}
	if (!divisor) {
		data.da[idx] = temp.join('');
	} else {
		data.da[idx] = parseInt(temp.join(''))/divisor;
	}
	idx++;
	return lineArr;
}

function testDataDecode(command, inputArr){
	switch (command) {
	case 'c880': //battery voltage V
		var temp=[];
		for (var i = 0; i<=2; i++){
			temp.unshift(inputArr.shift()); //10750500 -> 00057510\
		}
		var count = parseInt(temp.join(''))/1000; //00057510 -> 57.51
		data.di[idx] = "battery_volt";
		data.da[idx] = count;
		//data.battery_volt = count;
		break;
	case 'c881': //battery charge current ...