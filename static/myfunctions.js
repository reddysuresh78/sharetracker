

function show() {

$(document).ajaxStart(function(){
    $.LoadingOverlay("show");
});
$(document).ajaxStop(function(){
    $.LoadingOverlay("hide");
});
 
 
$.ajax({
  type: 'GET',
  //url: 'http://localhost:8020/refreshGainers' ,
  url: 'http://localhost:8020/refreshGainers' ,
  dataType: 'json',
 
		
  success: function (response) {
	                  
	  
	  var trHTML = '';
	  trHTML += "<tr><th>BKT</th> <th>Symbol</th> <th>Gain</th> <th>CMP</th> <th>High</th> <th>BQty</th> <th>SQty</th> <th>Vol?</th> <th>New?</th> <th>Inc?</th></tr>"
				
	  $.each(response, function(key, value) {
		  
		  $.each(value, function(key1, value1) {
			  if(value1['buyIndicator'] == 'Y' || value1['newEntrant'] == 'Y' || value1['increased'] == 'Y') {
				  trHTML += '<tr class="table-success"><td><strong>' + key +   '</strong></td>' 
			  }else{
				  trHTML += '<tr><td><strong>' + key +   '</strong></td>' 
			  }
			  
			  
			  trHTML += '<td>' + value1['symbol'] +  ' </td> ' + '<td>' + value1['gain'] +  ' </td> ' + '<td>' + value1['curPrice'] +  ' </td> ' + '<td>' + value1['dayHigh'] +  ' </td> '+ '<td>' + value1['buyQuantity'] +  ' </td> ' + '<td>' + value1['sellQuantity'] +  ' </td> ' + '<td>' + value1['buyIndicator'] +  ' </td> ' + '<td>' + value1['newEntrant'] +  ' </td> '  
			  
			  if( value1['increased'] == 'Y' ){ 
				trHTML +=  '<td class="bg-primary">' + value1['increased'] +  ' </td> ' 
			  }else{
				trHTML +=  '<td class="bg-warning">' + value1['increased'] +  ' </td> '   
			  }
			  trHTML += '</tr>'
		  });
		  
	});
	
    $('#added-articles').html(trHTML); 
	 

  },
  error: function(data){
    //if error
    console.log("ERROR: " + data);
	$('#shares').html(response); 
	}
});
 
                 
}