%from datetime import datetime
%from bottle import request
<html>
<head>
	<script src="//ajax.googleapis.com/ajax/libs/jquery/1.9.1/jquery.min.js"></script>
	<link rel="stylesheet" type="text/css" href="/static/style.css">	
</head>
<body>	
	<nav class="navigation">
		<ul class = "nav-section">
			<li>
				
				<a href ="/channels/create" class = "nav-link" id ="subscribe-link">
					<i class = "icon-plus"></i>
					Subscribe
				</a>				
			</li>	
		</ul>
		<ul class = "nav-section">			
			<li>
				<a href = "/items" id ="all" class = "nav-link {{is_active('/items')}}">
					<i class = "icon-folder"></i>
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
					<i class = "icon-feed"></i>
					{{channel.title}}
					<span class = "not-important">({{channel.unread_count()}})</span>					
				</a>
				<a href = "/channels/{{channel.id}}/edit" class = "nav-dropdown"><i class = "icon-caret-down"></i></a>											
			</li>						
		%end
		</ul>	
	</nav>
	<dl class = "accordion" id = "content">
		%for item in items:
		<div class = "item">			
		<dt class = "{{"read" if item.read else ""}}">		    			
			<div class = "side">
				<span class = "not-important">{{item.updated.strftime('%H:%M') if (item.updated.date() == datetime.today().date()) else item.updated.strftime('%y-%m-%d')}}</span>
				<a class = "link" href = "{{item.url}}" target="_blank">
					<i class = "icon-external"></i>
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
		<dd class = "description" style = "display: none;">			
			{{item.description}}
			<span class = "author">by {{item.author}}</span>
		</dd>
		</div>		
		%end
		
		%if next:
			<a class = "page-link" href = {{next}} > Next &rarr; </a>
		%end
		%if prev:
		  <a class = "page-link" href = {{prev}} > &larr; Prev </a>	
		%end
	</dl>
	
	
	<div style="display:none" id = "modal" class ="popup"></div>		

</body>
</html>
<script>
		
	$(document).ready(function()
	{	
		$('.item .mark-read').click(function(event)
		{
			var item = $(this).parent().parent();
			item.toggleClass('read');
			event.preventDefault();			
			$.ajax({
				url: $(this).attr('href'),				
				data: '{"read" : ' + item.hasClass('read') + '}',				
				contentType: "application/json; charset=utf-8",
				type: 'PATCH',
				error: function()
				{					
					item.removeClass('read');
				}							
			});
		});
	
		$('.mark-star').click(function(event)
		{
			event.preventDefault();
			var element = $(this);
			element.find('i').toggleClass('icon-star');
			element.find('i').toggleClass('icon-star-empty');					
			$.ajax({
				url: '/items/' + element.data('id'),				
				data: '{"starred" : ' + !element.data('checked') + '}',				
				contentType: "application/json; charset=utf-8",
				type: 'PATCH',
				success: function()
				{					
					element.data('checked', !element.data('checked'));					
				},
				error: function()
				{
					element.find('i').toggleClass('icon-star');
					element.find('i').toggleClass('icon-star-empty');					
				}							
			});			
		});
		
		$('.delete').click(function(event)
		{
			event.preventDefault();
			var l = $(this);			
			$.get($(this).attr('href'), function(data){
				$('#modal').html(data).toggle();
				$('#modal').css('top', l.offset().top + l.height());
				$('#modal').css('left', l.offset().left + l.width());				
			});			
		});
		
		$('.nav-dropdown').click(function(event)
		{
			event.preventDefault();
			var l = $(this);			
			$.get($(this).attr('href'), function(data){
				$('#modal').html(data).toggle();
				$('#modal').css('top', l.offset().top + l.height());
				$('#modal').css('left', l.offset().left + l.width());				
			});			
		});
		
		$('.mark-read').click(function(event)
		{									
			cur_stus = $(this).parent().parent().attr('stus');
			if(cur_stus != "active") {
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
				$('#modal').css('top', l.offset().top + l.height());
				$('#modal').css('left', l.offset().left + l.width());
			});
		});
		
		$(document).mouseup(function (e) {
			var container = $(".popup");
			if (container.has(e.target).length === 0) {
				container.hide();
			}
		});
		
		$('.link').mousedown(function(e) {			
			if (e.which <= 2) {
			e.preventDefault();			
			var item = $(this).parent().parent();
			item.addClass('read');					
			$.ajax({
				url: item.find('.mark-read').attr('href'),				
				data: '{"read" : true}',				
				contentType: "application/json; charset=utf-8",
				type: 'PATCH',
				error: function()
				{					
					item.removeClass('read');
				}							
			});
			return true;
			}
		});
		
		$('.nav-dropdown').click(function() {
				var l = $(this);
				$('.dropdown', this).css('top', l.offset().top + l.height());
				$('.dropdown', this).css('left', l.offset().left + l.width());
				$('.dropdown',this).show();
		});
	});
</script>
