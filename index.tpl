%from datetime import datetime
%from bottle import request
<html>
<head>
	<script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
	<link href="//netdna.bootstrapcdn.com/font-awesome/3.1.1/css/font-awesome.css" rel="stylesheet">
	<link rel="stylesheet" type="text/css" href="/static/style.css">	
</head>
<body>	
	<nav class="navigation">
		<ul class = "actions">
			<li>
				
				<a href ="/channels/create" class = "nav-link" id ="subscribe-link">
					<i class = "icon-plus-sign"></i>
					Subscribe
				</a>				
			</li>	
		</ul>
		<ul class = "filters">			
			<li>
				<a href = "/items" id ="all" class = "nav-link {{is_active('/items')}}">
					<i class = "icon-folder-close-alt"></i>
					All
				</a>
				<a href = "/channels/update" class= "update">&nbsp;</a>
			</li>
			<li>
				<a href = "/items?starred=1" id = "starred" class = "nav-link {{is_active('/items?starred=1')}}">
					<i class = "icon-star"></i>
					Starred
				</a>
			</li>
		</ul>
		<ul class = "channels">			
		%for channel in channels:		
			<li>			
				<a href = "/channels/{{channel.id}}/items" class = "nav-link {{is_active("/channels/" + str(channel.id) + "/items")}}">
					<i class = "icon-rss-sign"></i>
					{{channel.title}}
					<span class = "unread-count">({{channel.unread_count()}})</span>					
				</a>
				<ul class = "nav-dropdown">
				<a href = "#"><i class = "icon-caret-down"></i></a>
				<ul class= "dropdown popup">
					<li>
						<a href = "/channels/{{channel.id}}/update" class= "update">
						<i class = "icon-refresh"></i>
						Update
						</a>
					</li>
					<li>
						<a href = "/channels/{{channel.id}}/delete" class = "delete">
							<i class = "icon-remove"></i>
							Delete
						</a>
					</li>
				</ul>
				</ul>								
			</li>						
		%end
		</ul>	
	</nav>
	<dl class = "accordion" id = "content">
		%for item in items:
		<div class = "item">			
		<dt class = "{{"read" if item.read else ""}}">		    			
			<div class = "side">
				<span>{{item.updated.strftime('%H:%M') if (item.updated.date() == datetime.today().date()) else item.updated.strftime('%y-%m-%d')}}</span>
				<a class = "link" href = "{{item.url}}" target="_blank">
					<i class = "icon-external-link-sign"></i>
				</a>
			</div>
			
			<div class = "header">
				<a class = "mark-star" data-id = "{{item.id}}" data-checked = "{{"true" if item.starred else "false"}}"  href ="/items/{{item.id}}">
					<i class = {{"icon-star" if item.starred else "icon-star-empty"}}></i>				
				</a>
			   
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
	<div style="display:none" id = "modal" class ="popup"></div>		

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
			var l = $(this);			
			$.get($(this).attr('href'), function(data){
				$('#modal').html(data).toggle();
				$('#modal').css('top', l.position().top + l.height());				
			});			
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
		$('#subscribe-link').click(function(event){
			event.preventDefault();
			var l = $('#subscribe-link')			
			$.get($('#subscribe-link').attr('href'), function(data){
				$('#modal').html(data).toggle();
				$('#modal').css('top', l.position().top + l.height());
			});
		});
		
		$(document).mouseup(function (e) {
			var container = $(".popup");
			if (container.has(e.target).length === 0) {
				container.hide();
			}
		});
		
		$('.nav-dropdown').click(function(){
				$('.dropdown',this).fadeIn();
			});
	});
</script>
