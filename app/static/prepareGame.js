function checkGameType(o, gameType){
  console.log("------"+ gameType+ "----------------")
  console.log("------"+ (o[1][gameType] == "") + "----------------")
  var keys = Object.keys(o);
  var bool = true;
  if(o[1][gameType] == ""){
    var x = loop_through_games(o);
    console.log("undefined ----" + x)
    return loop_through_games(o);
  } else if (o[1][gameType].length == 0) {
    return loop_through_games(o);
  }
  for(var i=1;i<keys.length;i++){
    if(o[i][gameType] == undefined){
      bool=false;
      break;
    }
  }
  if (bool == true) {
    return gameType;
  }
  return loop_through_games(o);

  function loop_through_games(o){
    var g = ['translations',
      'definitions',
      'synonyms',
      'sentences']
    for (var i =g.length - 1; i >= 0;i--){
      var game = g[i];
      var type = o[1][game];
      console.log(game,type);
      if (type != undefined && !(jQuery.isEmptyObject(type))){
        return game;}
      }
    }
}

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
          console.log( "$.post('/game-win', {id: "+ window.oJson[1]['UWL_id']+ ", game_type:" + window.gameType + ", result:" + "result})")
          $.post('/game-win', {id: window.oJson[1]['UWL_id'], game_type:window.gameType, result:result})
          .done(function(data){
            var points = $("<h1 />", {
              text:data,class:"points"
            })
            $("#translation").after(points);
          })
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

function addWordButton(word){
  var button = $("<div />", {
      class: "add-button text-center",
      text:"Add this word to your list",
      click: function(e) {
        $.post('/add', {word:window.a}).done()//"{{ url_for('game') }}";
        e.preventDefault();
      }
      }
    )
  $("#progressBar").before(button);
}

function add_gameType(gameType){
  var d = $("<div />", {
    class:"game-type",
    text:"Find the " + gameType});
  var j = $(".jumbotron");
  j.prepend(d);
}

function game_colour(gameType) {
  var j = $(".jumbotron");
  var col = "#990033"
  if (gameType == "synonyms") {
    col = "#008099";
  }
  else if (gameType == "sentences") {
    col = "#660099";
  }
  else {return}
  j.css({"color":col});
}

function isTextLong(text){
  if (text.length > 25) {
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
