$(document).ready(function(){
  var uri = window.location;

  updateCurrentNavigationItem(uri);
});

function updateCurrentNavigationItem(uri){
  $('.navbar .nav li').each(function(i, item){
    nav_section = item.firstElementChild['href'].split('/')[1]; // [0]project / [1]section / [2-]...
    uri_section = uri.pathname.split('/')[1]; // [1]project / [2]section

    if(nav_section == uri_section)
    {
      $(item).addClass('active');
    }
  });
}
