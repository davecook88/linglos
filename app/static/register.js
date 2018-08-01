function checkOptions(){
  var natLang = $("#native_language");
  var targLang = $("#target_language");

  if (natLang.val() != "en") {
    $("#target_language option[value='es']").remove();
    $("#target_language option[value='de']").remove();
    $("#target_language option[value='fr']").remove();
    $("#target_language option[value='pt']").remove();
  }

  if (natLang.val() == "en") {
    if ($("#target_language option[value='es']").length == 0){
      targLang.append('<option value="es">Spanish</option>');
      targLang.append('<option value="fr">French</option>');
      targLang.append('<option value="de">German</option>');
      targLang.append('<option value="pt">Portuguese</option>');
    }
  }
}
$("#native_language").click(checkOptions);
$("#target_language").click(checkOptions);
