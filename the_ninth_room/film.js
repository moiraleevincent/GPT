"use strict";
/* THE NINTH ROOM — original vector cinema. Every frame is drawn deterministically. */
const SVG="http://www.w3.org/2000/svg";
const art=document.getElementById("art");
const audio=document.getElementById("soundtrack");
const curtain=document.getElementById("curtain");
const subtitle=document.getElementById("subtitle");
const playBtn=document.getElementById("play");
const seek=document.getElementById("seek");
const statusEl=document.getElementById("status");
const timeEl=document.getElementById("time");
let G=art, shots=[], duration=0, current=0, playing=false, audioReady=false;
let lastFrame=performance.now(), lastPaint=-1, lastIndex=-1;

function n(tag,attrs={},parent=G){
  const e=document.createElementNS(SVG,tag);
  for(const [k,v] of Object.entries(attrs))e.setAttribute(k,String(v));
  parent.appendChild(e);return e;
}
function rect(x,y,w,h,fill,stroke="none",sw=1,rx=0){return n("rect",{x,y,width:w,height:h,fill,stroke,"stroke-width":sw,rx});}
function path(d,fill="none",stroke="none",sw=1,opacity=1){return n("path",{d,fill,stroke,"stroke-width":sw,opacity});}
function circ(cx,cy,r,fill,stroke="none",sw=1){return n("circle",{cx,cy,r,fill,stroke,"stroke-width":sw});}
function ellipse(cx,cy,rx,ry,fill,stroke="none",sw=1){return n("ellipse",{cx,cy,rx,ry,fill,stroke,"stroke-width":sw});}
function line(x1,y1,x2,y2,stroke="#886653",sw=2){return n("line",{x1,y1,x2,y2,stroke,"stroke-width":sw});}
function txt(x,y,s,size=26,fill="#463e35",spacing=0,anchor="middle"){
  const e=n("text",{x,y,fill,"font-family":"Georgia,Times New Roman,serif","font-size":size,"text-anchor":anchor,"letter-spacing":spacing});
  e.textContent=String(s);return e;
}
function group(transform="",opacity=1){return n("g",{transform,opacity});}
function within(transform,draw,opacity=1){const prev=G;G=group(transform,opacity);draw();G=prev;}
function gradient(parent,id,stops){
  let g=n("linearGradient",{id,x1:"0%",y1:"0%",x2:"0%",y2:"100%"},parent);
  for(const [at,color] of stops)n("stop",{offset:at,"stop-color":color},g);
}
function initialize(){
  const defs=n("defs",{},art);
  gradient(defs,"sky",[["0%","#29494f"],["100%","#9a9e86"]]);
  gradient(defs,"gold",[["0%","#f9d99b"],["48%","#bb8e58"],["100%","#e4bf7d"]]);
  gradient(defs,"door",[["0%","#8b4949"],["100%","#4e2e39"]]);
  gradient(defs,"wall",[["0%","#c8d3be"],["100%","#abc5b3"]]);
  const p=n("pattern",{id:"paperwall",width:68,height:68,patternUnits:"userSpaceOnUse"},defs);
  let old=G;G=p;rect(0,0,68,68,"#c9d6c5");path("M34 3Q12 22 34 34Q56 46 34 65Q12 46 34 34Q56 22 34 3","none","#7b9c8d",2,.5);circ(34,34,4,"#eddcbe");G=old;
  const st=n("pattern",{id:"stripes",width:84,height:140,patternUnits:"userSpaceOnUse"},defs);
  G=st;rect(0,0,84,140,"#d6d4b9");rect(35,0,14,140,"#b6c7ae");line(2,0,2,140,"#a7b7a4");G=old;
}
function cam(z=1,dx=0,dy=0){
  const e=art.querySelector("#camera");
  if(e)e.setAttribute("transform","translate(640 360) scale("+z.toFixed(4)+") translate("+(-640+dx).toFixed(2)+" "+(-360+dy).toFixed(2)+")");
}
function frame(){
  rect(21,20,1238,680,"none","#eee0be",2);
  rect(33,32,1214,656,"none","#48534b",1);
}
function label(s){txt(640,76,s,17,"#52665e",4);}
function character(x,y,size,kind,p,arm=0,blink=false,ghost=false){
  const vale=kind==="vale",coat=vale?"#714348":"#31515b",hair=vale?"#28272a":"#47352c";
  within("translate("+x+" "+(y+Math.sin(p*8+(vale?2:0))*1.5)+") scale("+size+")",()=>{
    ellipse(0,166,65,9,"#372e3040");
    path("M-35 100L-46 165H-10L-4 104M4 104L10 165H46L35 100","#292e2d");
    path("M-41 -17Q-68 -2-63 60L-51 138H51L63 60Q68 -2 41 -17Z",coat,"#283332",3);
    path("M-21 -13L0 42L21 -13","#f0e4d1");
    path("M0 20L-9 64L0 84L9 64Z",vale?"#c2a671":"#994947");
    within("rotate("+arm+" -50 0)",()=>{path("M-50 -10Q-82 25-75 108","none",coat,25);circ(-78,110,13,"#e3bea3");});
    within("rotate("+(-arm)+" 50 0)",()=>{path("M50 -10Q82 25 75 108","none",coat,25);circ(78,110,13,"#e3bea3");});
    rect(-13,-44,26,26,"#d9b79b");
    ellipse(0,-94,45,54,ghost?"#d3b5a0":"#e5c1a3","#a57f69",2);
    path(vale?"M-47 -112Q-43 -173 4 -153Q53 -160 48 -100L33 -140Q0 -121 -39 -127Z":"M-45 -110Q-47 -158-7 -156Q22 -167 44 -130Q16 -140 2 -133Q-22 -124 -40 -128Z",hair);
    if(vale)ellipse(42,-89,10,40,hair);
    if(blink){line(-23,-91,-8,-91,"#36332f",2);line(9,-91,23,-91,"#36332f",2);}
    else{ellipse(-14,-91,ghost?5:3,ghost?7:4,"#282e2f");ellipse(14,-91,ghost?5:3,ghost?7:4,"#282e2f");}
    path("M0 -89L-4 -70H4","none","#b18874",2);path("M-9 -56Q0 -53 9 -56","none","#946a61",2);
    if(vale){circ(-44,-81,3,"#dfba70");circ(44,-81,3,"#dfba70");}
  });
}
function clock(cx,cy,z){
  within("translate("+cx+" "+cy+") scale("+z+")",()=>{
    circ(0,0,70,"#614340","url(#gold)",9);circ(0,0,53,"#f1e0bd","#977b59",3);
    for(let i=0;i<12;i++){const a=i*Math.PI/6;line(Math.sin(a)*42,-Math.cos(a)*42,Math.sin(a)*49,-Math.cos(a)*49,"#625145",2);}
    path("M0 7V-39","none","#5a4740",4);path("M0 7V-46","none","#5a4740",2);circ(0,0,4,"#5d4a41");
  });
}
function facade(p,morning=false){
  rect(0,0,1280,720,morning?"#b6c9b7":"url(#sky)");
  circ(1093,103,50,morning?"#f5e5b7":"#ebe8d7");
  rect(0,577,1280,143,morning?"#889c83":"#2a4847");
  path("M240 578V147L640 76L1040 147V578Z","#dcac96","#694c4b",8);
  path("M226 147L640 55L1054 147","none","#753e40",31);
  line(224,158,1057,158,"#f0debe",11);line(260,190,1020,190,"#f8e3c4",4);
  for(let row=0;row<2;row++)for(let col=0;col<4;col++){
    let x=309+190*col,y=221+166*row;
    rect(x,y,99,130,"#f1d9ae","#8f6461",8,42);
    rect(x+13,y+14,73,101,morning?"#8fa8a1":((row+col)%3===0?"#335157":"#dcb57f"),"#8c6e62",3,29);
    line(x+49,y+14,x+49,y+114,"#ead1b2",5);line(x+14,y+69,x+85,y+69,"#ead1b2",4);
  }
  rect(494,166,292,38,"#405855","url(#gold)",4);
  txt(640,192,"HOTEL BELLWETHER",23,"#f5debb",2);
  rect(543,493,194,101,"#5e4442","#e8c99b",7,43);
  rect(609,513,62,80,"#1e3639","#c4a77a",4,24);
  rect(547,599,185,36,"#996a59","#e7bb8c",2);
  txt(640,624,"NO VACANCIES",17,"#f7e2c5",1.5);
  path("M73 589V238M1205 589V238","none","#243c3c",28);
  path("M75 335Q-4 296 37 214M1205 335Q1284 296 1243 214","none","#243c3c",29);
  if(morning){
    within("",()=>{
      const extra=group("",Math.max(0,1-Math.max(0,p-.56)*2.4));
      const prev=G;G=extra;
      rect(598,265,84,128,"#1b3031","#eed5a9",7,38);rect(612,282,56,94,"#101d1e");
      ellipse(640,333,21,29,"#ddc1a9");path("M619 323Q616 298 640 299Q662 300 664 323","#393334");
      ellipse(632,331,3,5,"#202527");ellipse(648,331,3,5,"#202527");
      G=prev;
    });
  }
  cam(1+p*.017,0,p*7);
}
function lobby(p){
  rect(0,0,1280,720,"url(#paperwall)");rect(0,448,1280,272,"#b89380");
  rect(0,414,1280,36,"#64766b");path("M0 720L570 448H710L1280 720Z","#d4bba0");
  for(let x of [135,1145]){rect(x-47,0,94,492,"#e7dcc0","#b0a38c",3);rect(x-61,25,122,26,"#935f56");}
  clock(640,220,1.13);
  rect(481,349,318,16,"#845650","#dbb379",4);
  txt(640,383,"THE OFFICE",19,"#5b4642",4);
  character(378,401,1.05,"felix",p,p>.5?6:0);
  character(907,401,1.05,"vale",p,0,p>.46&&p<.5);
  rect(202,513,876,157,"#884e4c","#44363b",7);
  rect(219,528,843,123,"none","#ddb27c",6);
  rect(564,529,152,59,"#dbc7a0","#7c5548",3);
  txt(640,568,"RECEPTION",24,"#684b43",3);
  path("M683 507Q686 475 707 480Q733 485 728 507","#c6a16b","#6d4d3d",3);
  ellipse(706,509,35,7,"#f0c57a");
  label("CHAPTER I : A PERFECT INVENTORY");cam(1+p*.014);
}
function keys(p){
  rect(0,0,1280,720,"#d5c7a8");
  rect(203,86,874,532,"#654541","#d7b785",13,6);rect(241,123,798,455,"#7a584e","#d6b68c",3);
  txt(640,172,"ROOM KEYS",38,"#f3dfbd",5);
  for(let i=0;i<9;i++){
    let col=i%3,row=Math.floor(i/3),x=394+244*col,y=229+121*row;
    line(x-99,y-17,x+90,y-17,"#a47b63",1.5);txt(x-72,y+20,String(i+1).padStart(2,"0"),20,"#f0d8b1",0,"start");
    circ(x+14,y-2,7,"#d4b075");
    const old=G;G=group("",i===8?Math.max(0,(p-.78)*4.6):1);
    if(i<8||p>.78){
      circ(x+14,y+28,15,"none","#e0b67a",5);
      path("M"+(x+14)+" "+(y+43)+"v35h12v-9h9v-10h-9","none","#e7bf83",6);
    }
    G=old;
  }
  rect(465,615,350,52,"#e7d3ad","#99775b",2);
  txt(640,649,"PLEASE RETURN YOUR KEY",20,"#795a48",2.5);
  cam(1.008+p*.035);
}
function dining(p){
  rect(0,0,1280,720,"url(#stripes)");
  rect(0,480,1280,240,"#b88d7a");path("M0 720L560 478H720L1280 720Z","#d7b8a2");
  rect(498,77,284,282,"#63796f","#c6a878",12,127);
  rect(516,95,248,244,"#ccb59b");
  txt(640,201,"THE",27,"#5e4840");txt(640,246,"DINING",36,"#5e4840");txt(640,297,"ROOM",29,"#5e4840");
  for(let x of [202,1078]){line(x,470,x,274,"#644940",14);line(x-35,329,x+35,329,"#644940",9);}
  ellipse(640,551,529,126,"#725048");ellipse(640,530,528,110,"#f3e6ce","#986651",15);
  for(let i=0;i<9;i++){
    let x=194+i*112,y=516+29*Math.abs(i-4)/4;
    ellipse(x,y,39,19,"#d6b78f","#b69c74",2);
    ellipse(x,y,29,13,"#fdf2dc","#cdbb9c",2);
    line(x-47,y-16,x-47,y+16,"#9a7952",3);line(x+47,y-16,x+47,y+16,"#9a7952",3);
  }
  line(640,474,640,345,"#a4804d",8);line(609,397,671,397,"#a4804d",7);
  for(let x of [616,640,664]){rect(x-5,334,10,38,"#f6e8c2");path("M"+x+" 332Q"+(x-13)+" 310 "+x+" 300Q"+(x+14)+" 312 "+x+" 332","#e3aa5e");}
  within("translate(0 "+(Math.max(0,p-.4)*71)+")",()=>{
    path("M883 650L881 615Q921 601 964 619L962 710","#664542","#c18a6b",10);
    line(899,617,898,694,"#d0a27a",6);line(942,618,942,696,"#d0a27a",6);
  });
  label("CHAPTER II : THE EXTRA PLACE");cam(1+p*.017);
}
function ledger(p,final=false){
  rect(0,0,1280,720,"#6e4a44");
  for(let i=0;i<12;i++)line(0,i*65,1280,i*65,"#7e574d",2);
  rect(171,64,940,583,"#a68d6c");
  rect(183,52,918,584,"#f2e1c1","#a18a68",4,4);
  line(238,161,1039,161,"#997d62",3);line(278,187,278,585,"#b9a68f",2);
  txt(640,125,"ARRIVALS & DEPARTURES",32,"#694f43",4);
  txt(319,197,"ROOM",17,"#7c6152",0,"start");
  txt(439,197,"GUEST",17,"#7c6152",0,"start");
  txt(1018,197,"STATUS",17,"#7c6152",0,"end");
  const names=["MRS. ARBOR","MR. HENLEY","MISS LEVINE","DR. STRAUSS","THE DUNN SISTERS","MR. GOULD","MRS. ROSE","MR. PELL"];
  for(let i=0;i<9;i++){
    const y=226+i*40;line(294,y+13,1032,y+13,"#c4b39a",1);
    txt(324,y,String(i+1).padStart(2,"0"),20,"#7e6351",0,"start");
    if(i<8){
      txt(437,y,names[i],22,"#5a5750",0,"start");
      txt(1015,y,"IN",17,"#777268",0,"end");
    }else{
      const old=G;G=group("",final?1:Math.max(0,(p-.35)*1.6));
      txt(437,y,"FELIX WARD",23,final?"#893e44":"#57504b",1.5,"start");
      txt(1018,y,final?"PERMANENT":"IN",16,final?"#913d40":"#706c64",0,"end");
      G=old;
    }
  }
  if(final){
    within("",()=>{
      let old=G;G=group("",Math.max(0,(p-.26)*2));
      line(762,589,1011,589,"#a05250",3);
      txt(1004,615,"NO DEPARTURE RECORDED",16,"#8c4544",1,"end");
      G=old;
    });
  }
  rect(153,58,22,575,"#50332e");rect(184,57,14,575,"#dfc7a6");
  cam(1+p*.05,0,6*p);
}
function corridor(p){
  rect(0,0,1280,720,"#29403d");
  path("M0 0H1280L854 205H426Z","#dcd1ac");
  path("M0 720H1280L854 370H426Z","#b18e7b");
  path("M0 0L426 205V370L0 720Z","#c0ceb7");
  path("M1280 0L854 205V370L1280 720Z","#c0ceb7");
  rect(426,205,428,165,"#c8d0bb","#e5d2ae",5);
  for(let side=0;side<2;side++)for(let i=0;i<4;i++){
    const w=108-i*16,x=side===0?24+i*99:1255-i*99-w,y=126+i*27,h=471-i*82;
    rect(x,y,w,h,"#81514c","#efd7ae",5-i*.65);
    rect(x+9,y+14,w-18,h-31,"none","#c29c75",2);
    circ(side===0?x+w-22:x+22,y+h*.55,Math.max(2,6-i),"#e8c58d");
    txt(x+w/2,y+32,side===0?i*2+1:i*2+2,Math.max(13,23-i*2),"#f0dbb4");
  }
  path("M552 371H728L931 720H349Z","#80414a","#d6b884",8);
  rect(557,222,166,146,"#61776b","#d5bd9d",5);
  txt(640,252,"STAFF ONLY",15,"#f0e0be",1.5);
  const old=G;G=group("",Math.max(0,(p-.23)*1.7));
  rect(579,265,122,121,"#542e38","#f0d4ac",8);
  rect(591,278,98,102,"#4c3039","#ba9374",3);
  txt(640,325,"09",33,"#e8c48e");circ(678,338,4,"#e6c088");
  G=old;
  cam(1+p*p*.20,0,-17*p);
}
function door(p){
  rect(0,0,1280,720,"url(#paperwall)");
  rect(0,570,1280,150,"#b28d7a");
  rect(344,65,592,656,"#e9dcbb","#a9906f",15);
  rect(402,110,476,599,"url(#door)","#e3ba85",12);
  rect(440,155,400,481,"none","#ab7967",9);
  rect(465,184,350,155,"none","#c09a78",4);
  rect(465,371,350,234,"none","#c09a78",4);
  txt(640,289,"09",108,"#f1d196",12);
  circ(785,467,26,"url(#gold)");circ(785,467,9,"#624239");
  rect(402,112,Math.max(0,(p-.58))*89,595,"#111c1d");
  path("M603 706L675 706L702 720H574Z","#121b1d","none",1,Math.max(0,p-.25));
  cam(1+p*.045);
}
function room(p){
  rect(0,0,1280,720,"url(#stripes)");
  rect(0,517,1280,203,"#96776b");rect(0,496,1280,22,"#dfc79e");
  for(let x of [121,1159])rect(x-28,0,56,525,"#e8d9b8","#bba281",4);
  rect(479,89,322,321,"#5c4546","#d3b37e",11,149);
  rect(507,116,265,266,"#3c5250","#c2a882",5,126);
  txt(640,184,"STAFF",25,"#edd8bd",1);txt(640,215,"PORTRAIT",21,"#edd8bd",2);
  path("M309 160V183L264 215L354 215","none","#65564e",6);
  path("M269 230L237 475H364L337 230L317 214L301 267L284 213Z","#325560","#1f3238",8);
  path("M303 250L300 365L313 389L325 365L314 250","#914b48");
  rect(730,426,383,167,"#795b57","#493739",7,19);
  rect(745,407,347,114,"#e5d9c1","#b7a58b",5,22);
  path("M756 474Q808 460 856 453Q912 "+(439-p*31)+" 944 453Q1001 460 1078 469L1084 510H752Z","#f1e6ce","#c7b69e",3);
  rect(83,511,297,115,"#88584f","#e1bf88",8,7);
  txt(229,574,"F. WARD",28,"#f4dfb5",3);
  line(134,547,327,547,"#d9b77e",4);line(134,596,327,596,"#d9b77e",4);
  let old=G;G=group("",Math.max(0,(p-.20)*1.7));
  ellipse(640,302,48,62,"#d8ba9d");
  path("M590 289Q586 239 639 237Q692 241 691 297Q660 267 618 276Z","#383237");
  ellipse(619,303,6,9,"#182527");ellipse(662,303,6,9,"#182527");
  path("M618 342Q640 344 662 341","none","#7b5c56",3);
  G=old;
  cam(1+p*.032);
}
function mirror(p){
  rect(0,0,1280,720,"#b5c8b6");
  rect(0,554,1280,166,"#b38d7d");
  for(let x of [164,1116])rect(x-55,0,110,596,"#e9dcb9","#b49b7f",5);
  ellipse(638,346,244,311,"#8a5d54","#ebc68d",24);
  ellipse(638,346,209,275,"#77958e","#bed0b5",6);
  path("M520 117Q579 94 649 102","none","#e8e4c5",10,.3);
  character(638,389,1.13,"felix",p,p>.44?Math.min(72,(p-.44)*113):0,p>.18&&p<.26,true);
  ellipse(638,346,208,275,"none","#dbc49d",5);
  character(153,417,.92,"felix",p,0);
  character(1114,417,.92,"vale",p,0,p>.61&&p<.68);
  cam(1+p*.03);
}
function titleCard(p){
  rect(0,0,1280,720,"#c6b7a1");
  rect(67,53,1146,614,"#e7d6b9","#67534c",5);
  rect(85,73,1110,571,"none","#a5826a",3);
  line(640,87,640,216,"#a5826a",3);line(640,516,640,635,"#a5826a",3);
  line(175,365,350,365,"#a5826a",3);line(933,365,1105,365,"#a5826a",3);
  txt(640,257,"THE NINTH",82,"#673f41",7);
  txt(640,371,"ROOM",117,"#673f41",17);
  line(440,411,839,411,"#a5826a",3);
  txt(640,455,"HOTEL BELLWETHER · EST. 1931",21,"#67564c",3);
  txt(640,574,"IN THREE INCONVENIENT PARTS",17,"#67564c",4);
  cam(1+p*.011);
}
function endCard(p){
  rect(0,0,1280,720,"#273d3e");
  rect(110,65,1060,590,"none","#d1ac76",3);
  rect(130,83,1020,550,"none","#849b87",2);
  for(let x of [178,1102])for(let y of [146,581])path("M"+(x-29)+" "+y+"Q"+x+" "+(y-34)+" "+(x+29)+" "+y+"Q"+x+" "+(y+34)+" "+(x-29)+" "+y,"none","#c4a075",2);
  txt(640,247,"THE NINTH ROOM",69,"#f3dcbc",6);
  line(388,275,892,275,"#d0ad7a",3);
  txt(640,344,"A FILM BY THE REGISTRY",23,"#e4d3b2",4);
  txt(640,409,"NO VACANCIES",36,"#eacb99",6);
  txt(640,553,"THE END",20,"#d6b88b",5);
  if(p>.68)txt(640,591,"PLEASE CHECK IN AGAIN",13,"#829d91",4);
}
function paintScene(s,p){
  art.replaceChildren();initialize();
  const root=G=group("",1);root.id="camera";
  switch(s.scene){
    case "title":titleCard(p);break;
    case "facade":facade(p);break;
    case "facade_final":facade(p,true);break;
    case "lobby":lobby(p);break;
    case "keys":keys(p);break;
    case "dining":dining(p);break;
    case "ledger":ledger(p);break;
    case "ledger_final":ledger(p,true);break;
    case "corridor":corridor(p);break;
    case "door":door(p);break;
    case "room":room(p);break;
    case "mirror":mirror(p);break;
    case "end":endCard(p);break;
    default:rect(0,0,1280,720,"#243c3a");
  }
  G=art;frame();
}
function formatTime(v){let s=Math.max(0,Math.floor(v));return Math.floor(s/60)+":"+String(s%60).padStart(2,"0");}
async function load(){
  try{
    let r=await fetch("script.json");if(!r.ok)throw Error("Script unavailable");
    const script=await r.json();let timeline=null;
    try{r=await fetch("timeline.json?v=2");if(r.ok)timeline=await r.json();}catch(_){}
    if(timeline&&timeline.shots&&timeline.shots.length===script.length){
      shots=timeline.shots;duration=timeline.duration;
      statusEl.textContent="Kokoro cast · original stereo score · headphones recommended";
    }else{
      let cursor=0;shots=script.map(s=>{let start=cursor;cursor+=s.duration;return {...s,start,end:cursor};});
      duration=cursor;statusEl.textContent="Visual cut ready · Kokoro audio rendering";
    }
    seek.max=Math.round(duration*100);seek.step="1";render(true);
  }catch(e){statusEl.textContent="Unable to open the guest register";console.error(e);}
}
audio.addEventListener("canplay",()=>{audioReady=true;statusEl.textContent="Kokoro cast · original stereo score · headphones recommended";});
audio.addEventListener("error",()=>{audioReady=false;if(shots.length)statusEl.textContent="Visual edition ready · audio awaiting render";});
audio.addEventListener("ended",()=>{playing=false;current=duration;playBtn.textContent="Replay";render(true);});
function shotIndex(t){
  let lo=0,hi=shots.length-1;
  while(lo<hi){const mid=(lo+hi)>>1;if(t>=shots[mid].end)lo=mid+1;else hi=mid;}return lo;
}
function render(force=false){
  if(!shots.length)return;
  current=Math.min(duration,Math.max(0,current));
  const ix=shotIndex(Math.min(current,duration-.001)),s=shots[ix];
  const p=Math.max(0,Math.min(1,(current-s.start)/(s.end-s.start)));
  if(force||ix!==lastIndex||Math.abs(current-lastPaint)>.034){
    paintScene(s,p);lastPaint=current;lastIndex=ix;
    subtitle.replaceChildren();
    if(s.text){const span=document.createElement("span");span.textContent=s.text;subtitle.appendChild(span);}
    seek.value=Math.round(current*100);
    timeEl.textContent=formatTime(current)+" / "+formatTime(duration);
  }
}
function animate(now){
  const delta=Math.min(.10,(now-lastFrame)/1000);lastFrame=now;
  if(playing){
    if(audioReady&&!audio.paused&&Number.isFinite(audio.currentTime))current=audio.currentTime;
    else current+=delta;
    if(current>=duration){current=duration;playing=false;playBtn.textContent="Replay";}
    render();
  }
  requestAnimationFrame(animate);
}
async function start(){
  if(!shots.length)return;
  if(current>=duration-.2){current=0;try{audio.currentTime=0;}catch(_){}}
  curtain.classList.add("hide");playing=true;playBtn.textContent="Pause";
  try{audio.currentTime=current;await audio.play();audioReady=true;}catch(_){audioReady=false;statusEl.textContent="Subtitled visual edition";}
  lastFrame=performance.now();
}
function pause(){playing=false;audio.pause();playBtn.textContent="Play";}
document.getElementById("begin").addEventListener("click",start);
playBtn.addEventListener("click",()=>playing?pause():start());
document.getElementById("restart").addEventListener("click",()=>{current=0;try{audio.currentTime=0;}catch(_){}render(true);if(!playing)playBtn.textContent="Play";});
seek.addEventListener("input",e=>{current=Math.min(duration,Number(e.target.value)/100);if(audioReady){try{audio.currentTime=current;}catch(_){}}render(true);});
document.getElementById("mute").addEventListener("click",e=>{audio.muted=!audio.muted;e.target.textContent=audio.muted?"Sound off":"Sound on";});
document.getElementById("fullscreen").addEventListener("click",()=>{const box=document.querySelector(".frame");if(document.fullscreenElement)document.exitFullscreen();else if(box.requestFullscreen)box.requestFullscreen().catch(()=>{});});
window.addEventListener("keydown",e=>{
  if(e.code==="Space"&&e.target.tagName!=="BUTTON"&&e.target.tagName!=="INPUT"){e.preventDefault();playing?pause():start();}
  if(e.code==="ArrowRight"||e.code==="ArrowLeft"){current=Math.max(0,Math.min(duration,current+(e.code==="ArrowRight"?5:-5)));if(audioReady)audio.currentTime=current;render(true);}
});
load();requestAnimationFrame(animate);
