/**
 * Created by Mohamed Oun on 31-May-17.
 */
function loadPoster( theurl,counter) {
    var settings = {
  "async": true,
  "crossDomain": true,
  "url":theurl,
  "method": "GET",
  "headers": {},
  "data": "{}"
}
$.ajax(settings).done(function (response) {

    for(key in response){
        if (response[key].length>0) {
            result = key
            break;
        }
    }
     if (result == 'tv_episode_results')
            poster = 'still_path'
       else
            poster = 'poster_path'
  var path=response[result][0][poster];
  var href='https://image.tmdb.org/t/p/w92'+path;
    document.getElementById('poster'+counter).src = href;


});
}
function search() {
  // Declare variables
  var input, filter, table, tr, td, i;
  input = document.getElementById("myInput");
  filter = input.value.toUpperCase();
  table = document.getElementById("myTable");
  tr = table.getElementsByTagName("tr");

  // Loop through all table rows, and hide those who don't match the search query
  for (i = 0; i < tr.length; i++) {
    td = tr[i].getElementsByTagName("td")[2];
    if (td) {
      if (td.innerHTML.toUpperCase().indexOf(filter) > -1) {
        tr[i].style.display = "";
      } else {
        tr[i].style.display = "none";
      }
    }
  }
}