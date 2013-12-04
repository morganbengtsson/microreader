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
			<li>
				
				<a href ="/channels/import" class = "nav-link" id ="import-link">
					<i class = "icon-import"></i>
					Import
				</a>				
			</li>		
		</ul>
		<ul class = "nav-section">			
			<li>
				<a href = "/items" id ="all" class = "nav-link {{is_active('/items')}}">
					<i class = "icon-folder"></i>
					All
				</a>				
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
				<a href = "/channels/{{channel.id}}/items" class = "nav-link {{is_active("/channels/" + str(channel.id) + "/items")}} {{'has-new' if channel.new else ''}}">
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
				<a class = "link" href = "{{item.url}}" target="_blank" data-id = "{{item.id}}">
					<i class = "icon-external"></i>
				</a>
			</div>
			
			<div class = "header">
				<a class = "mark-star" data-id = "{{item.id}}" data-checked = "{{"true" if item.starred else "false"}}"  href ="/items/{{item.id}}">
					<i class = {{"icon-star" if item.starred else "icon-star-empty"}}></i>				
				</a>			 
				<span class = "mark-read" data-id="{{item.id}}">		    
					<h2 class="title {{'new-item' if item.new else ''}}" id = {{item.id}}>{{item.title}}</h2>
					 -
					<span class="summary">
						{{!item.description}}
					</span>
				</span>				
			</div>
						
		</dt>
		<dd class = "description" data-id = "{{item.id}}" style = "display:none;">			
			{{!item.description_html}}
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

		// $('dd').hide();	
		// if(window.location.hash) {
		// 	$(window.location.hash).parent().parent().parent().next().show();
						
		// }
		
		// window.onhashchange = function(){
		// 	$('dd').hide();	
		// 	$(window.location.hash).parent().parent().parent().next().show();
		// 	return true;
		// }

		$('.item .mark-read').click(function(event)
		{
			// show description
			var id = $(this).attr('data-id');
			var e = 'dd[data-id="' + id + '"]';
			if ($(e).is(":hidden")) {
				// only show this element
				$('dd').hide();
				$(e).show();
			} else {
				$(e).hide();
			}
			
			var item = $(this).parent().parent();
			item.addClass('read');
			//event.preventDefault();			
			$.ajax({
				url: '/items/' + $(this).attr('data-id'),				
				data: '{"read" : ' + true + '}',				
				contentType: "application/json; charset=utf-8",
				type: 'PATCH',
				error: function()
				{					
					item.removeClass('read');
				}							
			});
			return true;
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
		
		$('.nav-dropdown').click(function(event)
		{
			event.preventDefault();
			var l = $(this);	
			l.addClass("active-modal");		
			$.get($(this).attr('href'), function(data){
				$('#modal').html(data).show();
				$('#modal').css('top', l.offset().top + l.height());
				$('#modal').css('left', l.offset().left + l.width());				
			});			
		});		
		
		$('#modal').on('click','.delete',function(event)
		{
			event.preventDefault();
			var l = $(this);			
			$.get(l.attr('href'), function(data){
				$('#modal').html(data).show();			
			});			
		});
		
		$('#subscribe-link').click(function(event){
			event.preventDefault();
			var l = $(this);
			l.addClass("active-modal");			
			$.get(l.attr('href'), function(data){
				$('#modal').html(data).show();
				$('#modal').css('top', l.offset().top + l.height());
				$('#modal').css('left', l.offset().left + l.width());
			});
		});
		
		$('#import-link').click(function(event){
			event.preventDefault();
			var l = $(this);
			l.addClass("active-modal");			
			$.get(l.attr('href'), function(data){
				$('#modal').html(data).show();
				$('#modal').css('top', l.offset().top + l.height());
				$('#modal').css('left', l.offset().left + l.width());
			});
		});			
		
		$(document).mouseup(function (e) {
			var container = $(".popup");
			if (container.has(e.target).length === 0) {
				container.hide();
				$('a').removeClass('active-modal');		
			}
		});
		
		$('.link').mousedown(function(e) {			
			if (e.which <= 2) {
			e.preventDefault();			
			var item = $(this).parent().parent();
			item.addClass('read');					
			$.ajax({
				url: '/items/' + $(this).data('id'),				
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
