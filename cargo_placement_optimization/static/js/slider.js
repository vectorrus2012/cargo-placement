document.documentElement.setAttribute("lang", "ru");
document.documentElement.removeAttribute("class");

axe.run( function(err, results) {
  console.log( results.violations );
} );