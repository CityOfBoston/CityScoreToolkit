function toggle_visibility(id) {
   var e = document.getElementById(id);
   if(e.style.display == 'block')
      e.style.display = 'none';
   else
      e.style.display = 'block';
}

function toggle_arrow_span() {
    var e = document.getElementById('infobutton');
    var child = e.getElementsByTagName('span');
    if(child.class == "glyphicon glyphicon-chevron-up")
        child.class = "glyphicon glyphicon-chevron-down";
    else
        child.class = "glyphicon glyphicon-chevron-up";
}

document.getElementById('infobutton').onclick(function(){
    print("hihi");
    toggle_visibility('more_info');
    toggle_arrow_span();
});
