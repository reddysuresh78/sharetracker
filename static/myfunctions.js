

function getLatestList(gainers) {

$(document).ajaxStart(function(){
    $.LoadingOverlay("show");
});
$(document).ajaxStop(function(){
    $.LoadingOverlay("hide");
});

if(gainers)
	link = 'http://localhost:8020/refreshGainers'
else
	link = 'http://localhost:8020/refreshLosers'
 
$.ajax({
  type: 'GET',
  //url: 'http://localhost:8020/refreshGainers' ,
  url: link ,
  dataType: 'json',
 
		
  success: function (response) {
	                  
	  
	  var trHTML = '';
	  trHTML += "<tr class='table-active'><th>BKT</th> <th>Symbol</th> <th>Gain%</th><th>ActGain</th> <th>CMP</th> <th>High</th> <th>Low</th> <th>Close</th><th>BQty</th> <th>SQty</th> <th>New?</th> <th>Vol?</th>  <th>Inc?</th><th>Thres?</th><th>Score</th></tr>"
				
	  $.each(response, function(key, value) {
		  
		  $.each(value, function(key1, value1) {
			  if(value1['buyIndicator'] == 'Y' || value1['newEntrant'] == 'Y' || value1['increased'] == 'Y') {
				  if(value1['newEntrant'] == 'Y'){ 
					trHTML += '<tr class="table-danger"><td><strong>' + key +   '</strong></td>' 
				  }else{
					trHTML += '<tr class="table-success"><td><strong>' + key +   '</strong></td>'   
				  }
			  }else{
				  trHTML += '<tr><td><strong>' + key +   '</strong></td>' 
			  }
			  
			  
			  trHTML += '<td>' + value1['symbol'] +  ' </td> ' + '<td>' + value1['gain'] +  ' </td> ' + '<td>' + value1['gainVal'] +  ' </td> ' + '<td>' + value1['curPrice'] +  ' </td> ' + '<td>' + value1['dayHigh'] +  ' </td> '+ '<td>' + value1['dayLow'] +  ' </td> ' + '<td>' + value1['previousClose'] +  ' </td> '+ '<td>' + value1['buyQuantity'] +  ' </td> ' + '<td>' + value1['sellQuantity'] +  ' </td> ' + '<td>' + value1['newEntrant'] +  ' </td> ' + '<td>' + value1['buyIndicator'] +  ' </td> '  
			  
			  if( value1['increased'] == 'Y' ){ 
				trHTML +=  '<td  >' + value1['increased'] +  ' </td> ' 
			  }else{
				trHTML +=  '<td  >' + value1['increased'] +  ' </td> '   
			  }
			  if( value1['threshold'] == 'Y' ){ 
				trHTML +=  '<td  >' + value1['threshold'] +  ' </td> ' 
			  }else{
				trHTML +=  '<td  >' + value1['threshold'] +  ' </td> '   
			  }
			  
			  var score = 0
			  if(value1['newEntrant'] == 'Y') score ++;
			  if(value1['buyIndicator'] == 'Y') score ++;
			  if(value1['increased'] == 'Y') score ++;
			  if(value1['threshold'] == 'Y') score ++;
			   
			  
			  trHTML +=  '<td  >' + score +  ' </td> '   
			  trHTML += '</tr>'
		  });
		  
	});
	
    $('#added-articles').html(trHTML); 
	
	if(document.getElementById('autoRefresh').checked) {
		if(gainers)
			setTimeout(getLatestList(true), 60000);
		else
			setTimeout(getLatestList(false), 60000);
	} 

  },
  error: function(data){
    //if error
    console.log("ERROR: " + data);
	$('#shares').html(response); 
	}
});
 
                 
}