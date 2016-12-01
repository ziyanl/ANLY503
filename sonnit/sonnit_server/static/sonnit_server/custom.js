function upvote(id) {
    var request = new XMLHttpRequest();
    var url = "/rate/" + id + "/1";
    request.open("GET", url, true);
    // Send the proper header
    request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    
    request.onreadystatechange = function() {
        if(request.readyState == 4 && request.status == 200) {
            var old_score = document.getElementById("sonnet_score_" + id).innerHTML;
            var score_parts = old_score.split(":");
            var new_score = score_parts[0] + ": " + (parseInt(score_parts[1]) + parseInt(this.response));
            document.getElementById("sonnet_score_" + id).innerHTML = new_score;
        }
    }
    request.send();
}

function downvote(id) {
    var request = new XMLHttpRequest();
    var url = "/rate/" + id + "/0";
    request.open("GET", url, true);
    // Send the proper header
    request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    
    request.onreadystatechange = function(diff) {
        if(request.readyState == 4 && request.status == 200) {
            var old_score = document.getElementById("sonnet_score_" + id).innerHTML;
            var score_parts = old_score.split(":");
            var new_score = score_parts[0] + ": " + (parseInt(score_parts[1]) + parseInt(this.response));
            document.getElementById("sonnet_score_" + id).innerHTML = new_score;
        }
    }
    request.send();
}

