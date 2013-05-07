%from datetime import datetime
<html>
<head>
	<script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
	<link rel="stylesheet" type="text/css" href="/static/style.css">	
</head>
<body>
	<nav class="navigation">		
		<button href ="#" id ="subscribe">Subscribe</button>
		<form style ="display:none" action="/channels" method="POST">
		Url: <input type="text" name = "url" class="url"/>
		<input type="submit" value = "Add">
		</form>
		<ul class = "actions">
			<li><a href = "/" id ="all" class = "nav-link {{"active" if ("" == url) else ""}}">All</a></li>
			<li><a href = "/starred" id = "starred" class = "nav-link {{"active" if ("starred" == url) else ""}}">Starred</a></li>
		</ul>
		<ul class = "channels">			
		%for channel in channels:		
			<li>			
				<a href = "/{{channel.id}}" class = "nav-link {{"active" if (str(channel.id) == url) else ""}}">
					{{channel.title}}
					<span class="{{"new-count-" + str('max' if( channel.new_count() > 20) else channel.new_count())}}">&nbsp;</span>
				</a>
				<a href = "/channels/{{channel.id}}" class = "delete">&nbsp;</a>					
			</li>		
		%end
		</ul>	
	</nav>
	<dl class = "accordion" id = "content">
		%for item in items:
		<div class = "item">			
		<dt class = "{{"read" if item.read else ""}}">
		    			
			<div class = "side"> 
				<a class = "link" href = "{{item.url}}" target="_new">&nbsp;</a>
				{{item.updated.strftime('%H:%M') if (item.updated.date() == datetime.today().date()) else item.updated.strftime('%y-%m-%d')}}
			</div>
			
			<div class = "header">
				<a class = "mark-star {{"starred" if item.starred else "un-starred"}}" data-id = "{{item.id}}" data-checked = "{{"true" if item.starred else "false"}}"  href ="/items/{{item.id}}">&nbsp;</a>
			   
				<a class = "mark-read" href ="/items/{{item.id}}">		    
					<h2 class="title">{{item.title}}</h2>
					 -
				<span class="summary">
					{{!item.description}}
				</span>
				</a>
			</div>
						
		</dt>
		<dd class = "description">			
			{{item.description}}
			<span class = "author">by {{item.author}}</span>
		</dd>
		</div>		
		%end	
	</dl>

</body>
</html>
<script>
		
	$(document).ready(function()
	{
		$('.accordion dd').hide();	
		$('.item .mark-read').click(function(event)
		{
			var item = $(this).parent().parent();
			event.preventDefault();			
			$.ajax({
				url: $(this).attr('href'),				
				data: '{"read" : true}',				
				contentType: "application/json; charset=utf-8",
				type: 'PATCH',
				success: function()
				{					
					item.addClass('read');
				}							
			});
		});
		
		$('.mark-star').click(function(event)
		{
			event.preventDefault();
			var element = $(this);			
			$.ajax({
				url: '/items/' + element.data('id'),				
				data: '{"starred" : ' + !element.data('checked') + '}',				
				contentType: "application/json; charset=utf-8",
				type: 'PATCH',
				success: function()
				{
					element.toggleClass('starred');
					element.toggleClass('un-starred');
					element.data('checked', !element.data('checked'));	
				}							
			});			
		});
		
		$('.delete').click(function(event)
		{
			event.preventDefault();
			var element = $(this);	
			if (confirm('Are you sure?')){
				$.ajax({
					url: element.attr('href'),
					contentType: "application/json; charset=utf-8",
					type: 'DELETE',
					success: function()
					{
						element.parent().remove();	
					}							
				});
			}			
		});
		
		$('.mark-read').click(function(event)
		{									
			cur_stus = $(this).parent().parent().attr('stus');
			if(cur_stus != "active")
			{
				$('.accordion dd').hide();
				$('.accordion dt').attr('stus', '');			
				$(this).parent().parent().next().show();
				$(this).parent().parent().attr('stus', 'active');
			}
			return false;
		});
		$('#subscribe').click(function(){$('form').toggle()});
		$(document).mouseup(function (e)
{
		var container = $("form");

		if (container.has(e.target).length === 0)
		{
			container.hide();
		}
});
	});
</script>
