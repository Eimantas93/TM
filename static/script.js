// Set current date as default value and min value 
  $(document).ready(function() {
    var date = new Date();
    var day = date.getDate();
    var month = date.getMonth() + 1;
    var year = date.getFullYear();

    if (month < 10) month = "0" + month;
    if (day < 10) day = "0" + day;

    var today = year + "-" + month + "-" + day;       
    $("#theDate").attr("value", today);
    $("#theDate").attr("min", today);
// Need another ID for editing task (we don't need default value, just min value)
    $("#theDate2").attr("min", today);
// Need another ID for 'Start date' time (because same one doesn't work)
    $("#theDate3").attr("value", today);
    $("#theDate3").attr("min", today);
});

