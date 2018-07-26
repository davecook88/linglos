function checkGameType(o){
  var g = ['translations',
    'definitions',
    'synonyms',
    'sentences']
  for (var i =0; i<g.length;i++){
    var game = g[i];
    var type = o[1][game];console.log(game,type, type.length, type.length != 0);
    if (type.length != 0){console.log("IF STATEMENT", game);
    return game;}
  }}

function populateWordList(obj) {
  var keys = Object.keys(obj);
  var ary = []
  for(var i=1;i<keys.length;i++){
    var key = keys[i];
    if (obj[key][gameType] == undefined) {continue}
    var r = Math.floor(Math.random() * obj[key][gameType].length);
    var word = ( flip ? obj[key][options][r] : obj[key][options]);
    if (word != undefined){
      ary.push(word);
    }
  }
  return ary
}

function makeTranslationDiv(oJson) {
  var translation_number = Math.floor(Math.random() * oJson[1][gameType].length);
  var flip = oJson[0]["flip"]
  var translation = ( flip ? oJson[1][clue] : oJson[1][clue][translation_number]);
  var longTranslation = isTextLong(translation);
  $("#translation").text(translation);
  if (longTranslation) {
    $("#translation").addClass("small-translation");
  }
}

function makeAnswerDivs(oJson){
  listOfWords = shuffle(listOfWords);
  listOfWords.forEach(function(word,i) {
    var outerDiv = $("<div />", {
      class: "col-2-md",
    })
    var innerDiv = $("<div />", {
      class: "answer inner purple-hover",
      id: i,
      click: function(e) {
        if (!finished) {
          if ($(this).text() == a) {
            result = "win";
            win();
          } else {
            result = "lose";
            lose();
          }
          $.post('/game-win', {id: window.oJson[1]['UWL_id'], game_type:window.oJson[0]['game_type'], result:result}).done()
        }
        e.preventDefault();
      }
    })
    var answerText = '<span class="answer-text">' + word + '</span>'
    $(".answer-row").append(outerDiv);
    $(outerDiv).append(innerDiv);
    $(innerDiv).append(answerText)
    if (isTextLong(a)) {
      $(innerDiv).addClass("small-answer .full-height");
    }
  });
}

function isTextLong(text){
  if (text.length > 15) {
    return true;
  }
  return false;
}

function shuffle(array) {
  var currentIndex = array.length, temporaryValue, randomIndex;
  // While there remain elements to shuffle...
  while (0 !== currentIndex) {
      // Pick a remaining element...
      randomIndex = Math.floor(Math.random() * currentIndex);
      currentIndex -= 1;
      // And swap it with the current element.
      temporaryValue = array[currentIndex];
      array[currentIndex] = array[randomIndex];
      array[randomIndex] = temporaryValue;
  }
  return array;
}

function timeout(range, time, callback){
    var i = range[0];
    callback(i);
    Loop();
    function Loop(){
        setTimeout(function(){
            i++;
            if (i<range[1]){
                callback(i);
                Loop();
            }
        }, time)
    }
}

function countdown(timeLeft, maxTime) {
  var el = $("#progressBar > div");
  var percent = timeLeft/maxTime *  100;
  el.css("width",percent + "%");
  //el.animate({ width: percent +"%" }, 0.01);
}
