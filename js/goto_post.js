$(document).ready(function () {
  $('section.posts-expand').on('click', 'article', function (event) {
    var path = $(this).data('path');
    if (path) {
      // window.location.pathname = path;
      var win = window.open(path,'_blank');
      win.focus();
    }
  });
});