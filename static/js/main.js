$('.read-button').click(function(){
  var buttonLine = $(this).parent().parent();
  var href = buttonLine.children().eq(0).children().attr('href');
  $.ajax({
    type: 'POST',
    url: '/feed/read?url=' encodeURI(href),
    success: function(data){
      $(buttonLine).remove();
    }
  });
});

$('.read-all-button').click(function(){
  if(window.confirm('本当に全部読んだことにしていいですか？')){
    location.href = '/feed/read_all';
  }
});