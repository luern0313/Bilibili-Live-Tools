var storage = window.localStorage;
Date.prototype.format = function(fmt) {
    var o = {
        "M+": this.getMonth() + 1, //月份 
        "d+": this.getDate(), //日 
        "h+": this.getHours(), //小时 
        "m+": this.getMinutes(), //分 
        "s+": this.getSeconds(), //秒 
        "q+": Math.floor((this.getMonth() + 3) / 3), //季度 
        "S": this.getMilliseconds() //毫秒 
    };
    if (/(y+)/.test(fmt)) {
        fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
    }
    for (var k in o) {
        if (new RegExp("(" + k + ")").test(fmt)) {
            fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
        }
    }
    return fmt;
}

function recordPopularity() {
    var time = new Date();
    if (Math.floor(time.getTime() / 1000) % 5 == 0) {
        time = time.format("hh:mm:ss");
        var pop = document.evaluate("//*[@id='head-info-vm']/div/div/div[1]/div[2]/div[1]/span", document).iterateNext().innerText;
        var like = document.evaluate("//*[@id='head-info-vm']/div/div/div[1]/div[2]/div[2]/span", document).iterateNext().innerText;
        storage["temp_popularity"] = storage["temp_popularity"] + "," + time + " " + pop + ";" + like
        console.info(time + " " + pop + ";" + like);
        setTimeout(recordPopularity, 1000);
        return;
    }
    setTimeout(recordPopularity, 100);
}
