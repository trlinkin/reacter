$(document).ready(function(){
  var uri = window.location;

  updateCurrentNavigationItem(uri);
});

function updateCurrentNavigationItem(uri){
  $('.navbar .nav li').each(function(i, item){
    console.log(item.firstElementChild['href'].split('/'), uri.pathname.split('/'));
    nav_section = item.firstElementChild['href'].split('/')[2];
    uri_section = uri.pathname.split('/')[4];

    if(nav_section == uri_section)
    {
      $(item).addClass('active');
    }
  });
}
