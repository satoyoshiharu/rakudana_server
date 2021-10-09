/*
* Declarations of global variables
*/
let DEBUG = false;
let ws;
let logWs;
let imageCounter;
let numContacts;
let width;
let height;
let device;
//let utterance;
let voices;
let recognition;
let message_box = null;
let mode_box = null;
let display_box = null;
let message_cell = null;
let mode_cell = null;
let display_cell = null;
let action1_box = null;
let action1_cell = null;
let action2_box = null;
let action2_cell = null;
let action3_box = null;
let action3_cell = null;
let action4_box = null;
let action4_cell = null;
let action5_box = null;
let action5_cell = null;
let action6_box = null;
let action6_cell = null;
let action7_box = null;
let action7_cell = null;
let action8_box = null;
let action8_cell = null;
let action9_box = null;
let action9_cell = null;
let action10_box = null;
let action10_cell = null;
let action11_box = null;
let action11_cell = null;
let action12_box = null;
let action12_cell = null;
let contact1_box = null;
let contact1_cell = null;
let contact2_box = null;
let contact2_cell = null;
let contact3_box = null;
let contact3_cell = null;
let contact4_box = null;
let contact4_cell = null;
let contact5_box = null;
let contact5_cell = null;
let contact6_box = null;
let contact6_cell = null;
let contact7_box = null;
let contact7_cell = null;
let contact8_box = null;
let contact8_cell = null;
let contact9_box = null;
let contact9_cell = null;
let contact10_box = null;
let contact10_cell = null;
let contact11_box = null;
let contact11_cell = null;
let contact12_box = null;
let contact12_cell = null;
let serializer;
let button_active = true;
let sr_active = true;
let capability_sr = 0;
let capability_ss = 0;
let screen_width = 0;
let screen_height = 0;
let json = null;
let ss_ongoing = []; // FIFO queue
let contacts = [];

let sr_timer = 0;
let interval_timer;

let increment_sr_timer = function(){
  sr_timer += 100;
};

/*
* DOM update utilities
*/

function force_redraw(e) {
    let disp = e.style.display;
    e.style.display = 'none';
    let trick = e.offsetHeight; // force layout calc
    e.style.display = disp;
};

function clear_backgroundColor() {
    let imgs = document.getElementsByTagName('img');
    for (i of imgs) {
        i.parentNode.parentNode.parentNode.parentNode.style.backgroundColor = '#eeeeee';
    };
};

function clear(id) {
    let obj = document.getElementById(id);
    while (obj != null && obj.firstChild != null) { obj.removeChild(obj.firstChild); }
    return obj;
};

function newBox(name) {
    //console.log('newBox > '+name)
    let cell = document.createElement('div');
    cell.classList.add('cell');
    cell.id = name + "_cell";
    let box = document.createElement('div');
    box.classList.add('box');
    box.id = name + "_box";
    box.appendChild(cell);
    //console.log('newBox > ' + serializer.serializeToString(box));
    return [box, cell];
};

function show_mike_on() {
    console.log('show_mike_on...');
    if (capability_sr==0) return;
    let mode = clear('mode_cell');
    let img = new Image();
    img.src = MIKE_ON_ICON;
    img.style = "display: block; margin: auto; background-color:#fffffc;";
    if (mode != null) mode.appendChild(img);
    //console.log(serializer.serializeToString(document.getElementById('container')));
    //force_redraw(document.getElementById('body'));
};

function show_mike_off() {
    console.log('show_mike_off...');
    if (capability_sr==0) return;
    /*
    let mode = clear('mode_cell');
    let img = new Image();
    img.src = MIKE_OFF_ICON;
    img.style = "display: block; margin: auto; background-color:#fffffc;";
    mode.appendChild(img);
    */
    let mode = clear('mode_cell');
    let input = document.createElement('input');
    input.type = 'image';
    input.src = MIKE_OFF_ICON;
    input.setAttribute('onclick','enable_sr()');
    if (mode != null) mode.appendChild(input);
};

function grayout_button() {
    for (i=1; i<=json.suggestions.length; i++) {
        document.getElementById('Button'+i).style.backgroundColor="gray";
    };
};

/*
* Communication utilities
*/
async function connect() {
    console.log('connect...');
    ws = await new WebSocket(WSURL); // ws.readyState==CONNECTING
};

function connect_sync() {
    console.log('connect_sync...');
    ws = null;
    ws = new WebSocket(WSURL); // ws.readyState==CONNECTING
};

function safeSend(socket, param) {
    console.log('safeSend to ' + socket.url);
    switch (socket.readyState) {
        case socket.OPEN:
            socket.send(param);
            console.log('"'+ param + '"' + ' is sent');
            break;
        case socket.CONNECTING:
            console.log('websocket is CONNECTING and wait for OPEN');
            setTimeout( safeSend(socket, param), 500 );
            break;
        case socket.CLOSING:
        case socket.CLOSED:
            console.log('websocket is CLOSING or CLOSED');
            break;
    };
};

async function report_status(report) {
   if (ws.readyState==ws.OPEN) {
       let data = {};
       data['status'] = report;
       jsonData = JSON.stringify(data);
       ws.send(jsonData)
   };
}

async function Send() {
    if (capability_ss==1) speechSynthesis.cancel();
    if (capability_sr==1) recognition.stop();
    let data = {};
    data['action'] = 'send';
    data['contents'] = document.getElementById("textarea0").value;
    jsonData = JSON.stringify(data);
    console.log(jsonData);
    ws.send(jsonData)
};

async function sendRecognized(value) {
    if (capability_sr==0) return;
    let data = {};
    data['action'] = 'recognized';
    data['recognized'] = value;
    //data['timer'] = sr_timer.toString();
    jsonData = JSON.stringify(data);
    console.log(jsonData);
    ws.send(jsonData);
    if (DEBUG) report_status('Recognized after ' + sr_timer.toString() + ' milliseconds.');
};

/*
* Input controls
*/
function enable_button() {
    console.log('enable_button > ...');
    button_active = true;
}

function disable_button() {
    console.log('disable_button > ...');
    button_active = false;
};

async function enable_sr() {
    console.log('enable_sr > ...');
    if (capability_sr==1) {
        cancel_sr();
        cancel_ss();
        show_mike_on();
        sr_timer = 0;
        interval_timer = setInterval(increment_sr_timer, 100);
        sr_active = true;
        await start_recognition();
    };
};

function disable_sr() {
    console.log('disable_sr > ...');
    if (capability_sr==1) {
        cancel_sr();
        show_mike_off();
        clearInterval(interval_timer);
        sr_active = false;
    };
};

function cancel_sr() {
    console.log('cancel_sr > ...');
    if (capability_sr==1) {
        if (sr_active) {
            recognition.abort();
            recognition.stop();
        };
    };
};

function cancel_ss() {
    console.log('cancel_ss > ...');
    if (capability_ss==1) {
        console.log('ss_ongoing queue: '+ ss_ongoing.length)
        ss_ongoing = [];
        speechSynthesis.cancel();
    };
}

/*
* SS, SR handlers
*/
async function init_ss() {
    console.log('init_ss > ...')
    if (capability_ss==0) return;
    // each utterance is assigned its object, so that its onend event is distinguished by each.
    utterance = new SpeechSynthesisUtterance();
    //voices = window.speechSynthesis.getVoices();
    //utterance.voice = voices[7];
    utterance.volume = 1; //ボリューム
    utterance.rate = 1;  //レート
    utterance.pitch = 1; //ピッチ
    utterance.lang = 'ja-JP'; //言語
    return utterance;
};

async function init_sr() {
    console.log('init_sr > ...')
    if (capability_sr==0) return;
    SpeechRecognition = webkitSpeechRecognition || SpeechRecognition ;

    // looks not working
    // |
    // V
    //SpeechGrammarList = webkitSpeechGrammarList || SpeechGrammarList ;
    //const grammar = '#JSGF V1.0 utf-8 ja; grammar name; public <name> = あわの|いさむ;'
    //const speechRecognitionList = new SpeechGrammarList();
    //speechRecognitionList.addFromString(grammar, 1);
    //

    recognition = new SpeechRecognition();
    //recognition.grammars = speechRecognitionList;
    recognition.continuous = true;
    recognition.lang = 'ja-JP';
    recognition.interimResults = false;
    recognition.maxAlternatives = 5;
    recognition.stop();
}

async function speech(sentence) {
    console.log('speech > ' + sentence);
    if (capability_ss==0) return;
    //speechSynthesis.cancel();
    utterance = await init_ss();
    utterance.text = sentence;
    disable_sr();
    utterance.addEventListener('end', function(event) {
        status = 'Utterance finished after ' + event.elapsedTime + ' milliseconds.';
        console.log(status);
        //if (DEBUG) report_status(status);
        ss_ongoing.shift();
        //console.log('ss_ongoing.length:' + ss_ongoing.length);
    });
    //ss_ongoing.push(utterance);
    speechSynthesis.speak(utterance);
};

async function speech_and_reco(sentence) {
    console.log('speech and reco > ' + sentence);
    if (capability_ss==1) {
        //speechSynthesis.cancel();
        utterance = await init_ss();
        utterance.text = sentence;

        // This event may not occur on iPhone ???
        utterance.addEventListener('end', async function(event) {
            status = 'Utterance finished after ' + event.elapsedTime + ' milliseconds.';
            console.log(status);
            //if (DEBUG) report_status(status);
            ss_ongoing.shift();
            //console.log('ss_ongoing.length:' + ss_ongoing.length);
            if (capability_sr==1 && !sr_active) enable_sr();
        });

        disable_sr();
        //ss_ongoing.push(utterance);
        speechSynthesis.speak(utterance);
    };
};

async function start_recognition () {
    console.log('start_recognition > ...');
    if (capability_sr==0 || sr_active==false) return;

    recognition.onresult = async function (e) {
        console.log('recognition.onresult > ...');
        let value = e.results[0][0].transcript;
        console.log('onresult:'+value);
        /*for ( var i = e.resultIndex; i < e.results.length; ++i ) {
            console.log( e.results[i][0].transcript );
        };*/
        if (value!='あ' && value!='お') {
            await sendRecognized(value);
            disable_sr();
            disable_button();
        } else {
            recognition.abort();
            //if (!sr_active) enable_sr();
            // just ignore
            //let data = {};
            //data['error'] = 'nomatch';
            //jsonData = JSON.stringify(data);
            //ws.send(jsonData);
        }
    };

    recognition.onnomatch = async function (e) {
        // recognizer timeout <- user silent
        console.log('recognition.onnomatch...');
        recognition.abort();
        if (sr_timer<10000) {
            //recognition.start();
        } else {
            disable_sr();
            let data = {};
            data['error'] = 'nomatch';
            jsonData = JSON.stringify(data);
            ws.send(jsonData);
            if (DEBUG) report_status('No Match after ' + sr_timer.toString() + ' milliseconds.');
        };
    };

    recognition.onend = async function (e) {
        // 一定時間入力が無いと終了するので継続する
        if (DEBUG) report_status('recognition.onend...');
        console.log('onend');
        recognition.abort();
        disable_sr();
        //let data = {};
        //data['error'] = 'nomatch';
        //jsonData = JSON.stringify(data);
        //ws.send(jsonData);
    }

    recognition.onerror = async function (e) {
        if (DEBUG) report_status('recognition.onerror...');
        console.log('onerror');
        recognition.abort();
        //if (!sr_active) enable_sr();
        //let data = {};
        //data['error'] = 'nomatch';
        //jsonData = JSON.stringify(data);
        //ws.send(jsonData);
    };

    recognition.start();
};

/*
* Button event handlers
*/
function OnStartButton() {
    console.log('OnStartButton > ...');
    if (!button_active) return;

    if (!'SpeechSynthesisUtterance' in window) {
        //alert('Speech synthesis(音声合成) APIには未対応です.');
        capability_ss = 0;
    } else {
        capability_ss = 1;
    };
    console.log(capability_ss);
    if (!'SpeechRecognition' in window ||  typeof webkitSpeechRecognition === 'undefined'
        || location.protocol == 'http:') {
        //alert('Web Speech API には未対応です.');
        capability_sr = 0;
    } else {
        capability_sr = 1;
    };
    console.log(capability_sr);

    document.getElementById('start_button').style.backgroundColor="gray";
    //disable_button();
    //force_redraw(document.getElementById('body'));
    main();
    //ws.close();
    //window.close();
};

function setUpper(pCol) {
    message_box.style = 'grid-row: 1/2; grid-column:' + pCol + ';';
    mode_box.style = 'grid-row: 2/3; grid-column:' + pCol + '; background-color:#fffffc;';
    display_box.style = 'grid-row: 3/4; grid-column:' + pCol + '; background-color:#fffffc;';
    //mode_box.style = 'grid-row: 2/3; grid-column:' + pCol + ';';
    //display_box.style = 'grid-row: 3/4; grid-column:' + pCol + ';';
};

function addAction(fragment, num) {
    [box,cell] = newBox("action"+num.toString());
    //box.style = 'background-color:#fffffc; border-width:10pt;';
    box.style = 'border-width:10pt;';
    insertButton(cell,json.suggestions[num-1],"#c6d5ee7e",num); // cell in the box
    fragment.appendChild(box);
};

function addContactAction(fragment, num, span) {
    [box,cell] = newBox("action"+num.toString());
    box.style = 'background-color:#fffffc; border-width:10pt; grid-row=3/4; grid-column: span ' + span.toString() + ';';
    insertButton(cell,json.suggestions[num-1],"#c6d5ee7e",num); // cell in the box
    fragment.appendChild(box);
};

function addContact(fragment, num, flag) {
    console.log('addContact > num:' + num + ',flag:' + flag);
    [box,cell] = newBox("contact"+num.toString());
    box.style = 'display: table; width: 100%; height: 100%; grid-column: 2/6; background-color:#fffffc; grid-row-gap: 5px;';
    cell.style = "width:90%; font-size:3rem; background-color:" + "#c6d5ee7e" + "; border-width:10pt; cursol:pointer;";
    if (flag) {
        console.log('addContact > call case')
        //let a = document.createElement('a');
        url = 'tel://' + contacts[num-1]['number'];
        cell.innerHTML = '<a href="' + url + '">' + contacts[num-1]['name'] + '</a>';
        //console.log('addContact > ' + serializer.serializeToString(box));
        //cell.appendChild(a);
    } else {
        console.log('addContact > delete-from-contacts case')
        insertContact(cell,contacts[num-1],"#c6d5ee7e",num); // cell in the box
    };
    fragment.appendChild(box);
};

function insertButton(cell, label, bg, i) {
    let input = document.createElement('input');
    input.type = 'button';
    input.value = label;
    input.id = 'Button'+i;
    input.style = "width:90%; font-size:3rem; background-color:" + bg + "; border-width:10pt; cursol:pointer;";
    //input.style = "width:90%; font-size:3rem; border-width:10pt; cursol:pointer;";
    input.setAttribute('onclick','Button'+i+'()');
    cell.appendChild(input);
}

function insertContact(cell, contact, bg, i) {
    let input = document.createElement('input');
    input.type = 'button';
    input.value = contact['name'];
    input.id = 'Contact'+i;
    input.style = "width:90%; font-size:3rem; background-color:" + bg + "; border-width:10pt; cursol:pointer;";
    input.setAttribute('onclick','Contact'+i+'()');
    cell.appendChild(input);
}

function button_(num) {
    console.log('button_ > ' + num);
    if (!button_active) return;
    //grayout_button();
    b = document.getElementById('Button'+num);
    b.style.backgroundColor = "gray";
    disable_button();
    cancel_ss();
    disable_sr();

    let data = {};
    data['action'] = 'button';
    data['selection'] = num.toString();
    jsonData = JSON.stringify(data);
    console.log(jsonData);
    ws.send(jsonData)
}

function Button1() { button_(1); };
function Button2() { button_(2); };
function Button3() { button_(3); };
function Button4() { button_(4); };
function Button5() { button_(5); };
function Button6() { button_(6); };
function Button7() { button_(7); };
function Button8() { button_(8); };
function Button9() { button_(9); };
function Button10() { button_(10); };
function Button11() { button_(11); };
function Button12() { button_(12); };

function contact_button_(num) {
    console.log('contact_button_ > ' + num);
    if (!button_active) return;
    //grayout_button();
    b = document.getElementById('Contact'+num);
    b.style.backgroundColor = "gray";
    disable_button();
    cancel_ss();
    disable_sr();

    let data = {};
    data['action'] = 'button';
    data['selection'] = num.toString();
    jsonData = JSON.stringify(data);
    console.log(jsonData);
    ws.send(jsonData)
}

function Contact1() { contact_button_(1); };
function Contact2() { contact_button_(2); };
function Contact3() { contact_button_(3); };
function Contact4() { contact_button_(4); };
function Contact5() { contact_button_(5); };
function Contact6() { contact_button_(6); };
function Contact7() { contact_button_(7); };
function Contact8() { contact_button_(8); };
function Contact9() { contact_button_(9); };
function Contact10() { contact_button_(10); };
function Contact11() { contact_button_(11); };
function Contact12() { contact_button_(12); };

/*
* main and sub-routines
*/
async function sendCapability() {
    console.log('sendCapability > ...');
    let data = {};
    console.log(navigator.userAgent);
    if (navigator.userAgent.indexOf('iPhone') > 0)
        device = 'iPhone';
    else if (navigator.userAgent.indexOf('Android') > 0)
        device = 'Android';
    else
        device = 'pc';
    data['device'] = device;
    data['capability_ss'] = capability_ss.toString(10);
    data['capability_sr'] = capability_sr.toString(10);
    screen_width = window.parent.screen.width;
    data['screen_width'] = screen_width.toString(10);
    screen_height = window.parent.screen.height;
    data['screen_height'] = screen_height.toString(10);
    data['cookie'] = document.cookie;
    jsonData = JSON.stringify(data);
    console.log(jsonData);
    //ws.send(jsonData)
    safeSend(ws, jsonData);
};

async function wait_for_ssfinish() {
    console.log('wait_for_ssfinish > ...');
    if (device == 'iPhone') return; //on iPhone, ss finish event does not triggered - it's a bug.
    const sleep = (second) => new Promise(resolve => setTimeout(resolve, second * 1000))
    while (ss_ongoing.length>0) {
        await sleep(1);
    }
}

async function leave_action(json) {
    console.log('leave_action >')
    await wait_for_ssfinish();
    console.log('do');

    // On Safari, location.href doesn't work
    // http://wawawa12345.hatenablog.com/entry/2019/03/11/224034
    let ctn = document.getElementById('container');
    ctn.style = "display: grid; grid-template: 30vh 30vh 30vh / 20% 60% 20%;"
    let [display_box, display_cell] = newBox("display");
    display_box.style = 'grid-column:2/3; grid-row:2/3;';
    display_cell.style = "text-align:center; vertical-align:middle; font-size:3rem; margin 20pt; border-width:20pt; border-style:outset; border-color:light-gray gray light-gray gray; background-color:#c6d5ee7e;";
    display_cell.addEventListener('onclick', async function(event) {
        display_cell.style.backgroundColor = "gray";
    });
    let a = document.createElement('a');
    ws.close();
    disable_sr();

    switch (json.action) {
    case 'goto_url':
        console.log('leave_action > handles goto_url');

        while (ctn != null && ctn.firstChild != null) { ctn.removeChild(ctn.firstChild); }
        display_cell.innerHTML = '<a href="' + json.url + '"><h3>移動しないときはここをタップ</h3></a>';
        ctn.appendChild(display_box);

        location.replace(json.url);

        history.replaceState(null,null,"/www/doc/index.html");

        a.href = json.url;
        a.click();

        break;
    case 'invoke_app':
        console.log('leave_action > handles invoke_action');

        while (ctn != null && ctn.firstChild != null) { ctn.removeChild(ctn.firstChild); }
        // NOTE: Chrome requires human operation to invoke app link
        if ('guide' in json)
            display_cell.innerHTML='<a href="' + json.url + '"><h3>' + json.guide + '</h3></a>';
        else
            display_cell.innerHTML='<a href="' + json.url + '"><h3>ここをタップ</h3></a>';
        ctn.appendChild(display_box);

        location.replace(json.url);

        history.replaceState(null,null,"/www/doc/index.html");

        a.href = json.url;
        a.click();

        break;
    case 'finish':
        console.log('leave_action > handles finish');

        clear('container');
        history.replaceState(null,null,"/www/doc/index.html");
        window.close();
        break;
    //case 'set_cookie':
    //    document.cookie = json.cookie;
    //    break;
    };
};

async function main() {

    console.log('main...')

    //await connect();
    connect_sync();

    serializer = new XMLSerializer();
    if (capability_sr==1) await init_sr();
    //if (capability_ss==1) init_ss();

    ws.onopen = async (e) => {
        console.log('web socket connected');
        await sendCapability();
        document.getElementById('start_button').style.backgroundColor="gray";
        disable_button();
    };
    ws.onclose = async (e) => {
        console.log('web socket closed');
        //cancel_ss();
        cancel_sr();
    }
    ws.onerror = async (e) => {
        console.log('main> web socket onerror...');
        setTimeout(OnStartButton(), 1000);
    }
    ws.onmessage = async (e) => {
        console.log('main > ws.onmessage...')
        try
        {
            console.log('main > received:'+e.data);
            //if (capability_sr==1) recognition.abort();
            json = JSON.parse(e.data);

            if ('action' in json)
            {
                if (json.action=='set_cookie') {
                    document.cookie = json.cookie;
                } else {
                    console.log('main > ' + json.action);
                    await leave_action(json);
                }
            }
            else
            {
                // clear scene
                let ctn = clear('container');
                const fragment = document.createDocumentFragment();

                [message_box, message_cell] = newBox("message");
                if ('text' in json) message_cell.innerHTML='<p>'+json.text+'</p>';
                fragment.appendChild(message_box);

                [mode_box, mode_cell] = newBox("mode");
                fragment.appendChild(mode_box);

                if ('contacts' in json || 'delete' in json)
                {
                    console.log('main > contacts layout');

                    ctn.style = 'display: grid; grid-template-columns: 1fr 1fr 1fr 1fr 1fr 1fr; grid-template-rows: 15vh 10vh 15vh; grid-auto-rows: 100px';

                    // setUpper
                    message_box.style = 'grid-row: 1/2; grid-column: 1/7;';
                    mode_box.style = 'grid-row: 2/3; grid-column: 1/7; background-color:#fffffc;';

                    if ('suggestions' in json) {
                        console.log('main > contacts case, suggestions: '+ json.suggestions);
                        var num = json.suggestions.length;
                        for (i=0; i<num; i++) addContactAction(fragment, i+1, 6/num);
                    };

                    var contacts_str;
                    var contact_flag;
                    if ('contacts' in json) {
                        contacts_str = json.contacts;
                        contact_flag = true;
                    } else if ('delete' in json) {
                        contacts_str = json.delete;
                        contact_flag = false;
                    };
                    console.log('main > contacts:'+contacts_str);
                    var contactstrlist = contacts_str.split(',');
                    num = contactstrlist.length;
                    contacts = [];
                    for (i=0; i<num; i++) {
                        var nn = contactstrlist[i].split(':');
                        contacts[i] = {};
                        contacts[i]['name'] = nn[0];
                        contacts[i]['number'] = nn[1];
                        console.log(contacts[i]['name'])
                        console.log(contacts[i]['number'])
                        addContact(fragment, i+1, contact_flag);
                    };

                }
                else
                {
                    console.log('scene layout');

                    [display_box, display_cell] = newBox("display");
                    if ('image' in json) {
                        let img = new Image();
                        img.src = json.image;
                        //img.style = "display: block; margin: auto; background-color:#fffffc;";
                        img.style = "display: block; margin: auto;";
                        display_cell.appendChild(img);
                    };
                    if ('show' in json) display_cell.innerHTML='<p>'+json.show+'</p>';
                    fragment.appendChild(display_box);

                    if ('suggestions' in json) {
                        console.log('main > suggestions: '+ json.suggestions);
                        var num = json.suggestions.length;

                        if (num == 1) setUpper('1/2');
                        else if (num < 5) setUpper('1/3');
                        else setUpper('1/4');

                        sty = "display: grid; grid-template: ";
                        if (num == 1) ctn.style = sty + "15vh 10vh 35vh 30vh / 1fr;";
                        else if (num == 2) ctn.style = sty + "15vh 10vh 35vh 30vh / 1fr 1fr;";
                        else if (num < 5) ctn.style = sty + "15vh 10vh 35vh 15vh 15vh / 1fr 1fr;";
                        else if (num < 7) ctn.style = sty + "15vh 10vh 35vh 15vh 15vh / 1fr 1fr 1fr;";
                        else if (num < 10) ctn.style = sty + "15vh 10vh 20vh 15vh 15vh 15vh / 1fr 1fr 1fr;";
                        else ctn.style = sty + "15vh 10vh 5vh 15vh 15vh 15vh 15vh / 1fr 1fr 1fr;"

                        for (i=0;i<num;i++) addAction(fragment, i+1);
                        button_enable = true;
                    }
                    else {
                        console.log('0 suggestion, voice only prompt');
                        ctn.style = "display: grid; grid-template: 15vh 10vh 70vh / 1fr;";
                        setUpper('1/2');
                        fragment.appendChild(message_box);
                        fragment.appendChild(mode_box);
                        fragment.appendChild(display_box);
                    }

                }
                enable_button();
                ctn.appendChild(fragment);

                // talk
                if (capability_ss==1) {
                    ss_ongoing.push(json.feedback);
                    console.log('ss_ongoing.length:' + ss_ongoing.length);
                    if ('speech' in json) {
                        console.log('main > speech '+ json.speech);
                        await speech_and_reco(json.speech);
                    } else if ('feedback' in json) {
                        console.log('main > feedback '+ json.feedback);
                        await speech(json.feedback);
                    };
                };

                //let mode = document.getElementById('mode_cell');
                //mode.addEventListner('click', start_recognition()); //????????????????????????????
                //ws.send('done');
                //console.log(serializer.serializeToString(document.getElementById('container')));
            };
        } catch(exception) {
            console.log('exception:' + exception + ',' + json);
            report_status('ws.onMessage exception:' + exception + ','+json);
        };
    };
};
