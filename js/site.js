$(document).ready(function(){
  var uri = window.location;

  updateCurrentNavigationItem(uri);
});

function updateCurrentNavigationItem(uri){
  $('.navbar .nav li').each(function(i, item){
    uri_file = uri.pathname.split('/').pop();
    if(uri_file == 'reacter'){
      uri_file = 'index.html';
    }

    nav_file = item.firstElementChild['href'].split('/').pop();

    if(nav_file == uri_file)
    {
      $(item).addClass('active');
    }
  });
}
