var nextButton = $("<div />", {
    class: "inner next-button col-3-md purple-hover",
    text: "Next",
    click: function(e) {
      window.location.href=urls.game;//"{{ url_for('game') }}";
      e.preventDefault();
    }
  })

function lose(message) {
  var loseMessageText = message || "Sorry, wrong answer!";
  var loseMessage = $("<div />", {
    class: "col-12",
    text: loseMessageText,
  })
  var loseInner = $("<div />", {
    class: "wrong-answer-message inner",
    text: loseMessageText,
  })
  loseMessage = loseMessage.append(loseInner);
  finished = true;
  $(".win-lose-row").append(loseMessage);
  $(".answer").each(function(){
    highlightCorrectAnswer($(this));
    removePurpleHover($(this));
  });
  $(".win-lose-row").append(nextButton);

  function highlightCorrectAnswer(el) {
    text = $(el).text();
    if (text == a) {
      $(el).addClass("correct-answer");
      return;
    }};

    function removePurpleHover(el){
      $(el).removeClass("purple-hover");
    };

}
function win() {
  finished = true;
  $(".win-lose-row").append(nextButton);
}
