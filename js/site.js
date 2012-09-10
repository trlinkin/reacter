$(document).ready(function(){
  var uri = window.location;

  updateCurrentNavigationItem(uri);
});

function updateCurrentNavigationItem(uri){
  $('.navbar .nav li').each(function(i, item){
    nav_section = item.firstElementChild['href'].split('/')[4];
    uri_section = uri.pathname.split('/')[2];

    if(nav_section == uri_section)
    {
      $(item).addClass('active');
    }
  });
}
