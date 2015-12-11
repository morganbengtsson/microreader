%from datetime import datetime
%from bottle import request, url
%import os
<!DOCTYPE html>
<html>
<head>
	<script src="{{url("/static/<filename:path>", filename = "js/jquery-1.11.3.min.js")}}"></script>
	<link rel="stylesheet" type="text/css" href="{{url('/static/<filename:path>', filename='style.css')}}" />
	<link rel="icon" type="image/vnd.microsoft.icon" href="{{url('/static/<filename:path>', filename='favicon.ico')}}" />
</head>
<body>	
	<nav class="navigation">
		<form action="{{url('/items')}}" method="get">
		<ul class = "nav-section">
			<li>
				<a href ="{{url('/channels/create')}}" class="link" id ="subscribe">
					<button>Subscribe</button>
				</a>				
			</li>
			<li>
				<a href ="{{url('/channels/import')}}" class="link" id ="import">
					<button>Import</button>
				</a>				
			</li>		
		</ul>
		<ul class = "nav-section">			
			<li>
				<a class="link" href = "{{url('/items')}}" class = "{{is_active('/items')}}">
					All
				</a>				
			</li>
		</ul>
		<ul class = "channels nav-section">
		%for channel in channels:		
			<li>
                <input type="checkbox" name=channel value="{{channel.id}}" {{'checked' if channel.filter else ''}}>
                <a href = "{{url('/channels/<id:int>/edit', id=channel.id)}}" class = "link item-link nav-dropdown">
						<button>Settings</button>
				</a>
                <a href = "{{url('/channels/<id:int>/items', id=channel.id)}}"
                class = "background link {{is_active("/channels/" + str(channel.id) + "/items")}}
                {{'has-new' if channel.has_new() else ''}}" style="background-color: {{channel.color()}}">
					{{channel.title}}
				</a>
				<span class = "side">
					<span class = "not-important">({{channel.unread_count}})</span>
				</div>
			</li>						
		%end
		</ul>
		<button type="submit">Filter</button>
		</ul>
		</ul>
		</form>
	</nav>
	<dl class = "accordion" id = "content">
		%for item in items:
		<div class = "item">			
		<dt class = "{{"read" if item.read else ""}}">
			<span class = "header">
				<span class="actions">
				    <a class = "link item-link external-link" href = "{{item.url}}" target="_blank" data-id = "{{item.id}}">
					    Link
				    </a>,
				    <a href = "{{url('/channels/<id:int>/items', id=channel.id)}}"
                    class = "background link nav-link {{is_active("/channels/" + str(channel.id) + "/items")}}
                    {{'has-new' if channel.has_new() else ''}}" style="background-color: {{channel.color()}}">
                        {{channel.title[:3]}}
                    </a>:
			    </span>
				<a class = "title" href = '{{url('/items/<id:int>', id=item.id)}}' class = "mark-read" data-id="{{item.id}}">
					<span {{'new-item' if item.new else ''}}" id = {{item.id}}>
						{{item.title}}
					</span>
					-
					<span class="summary">
							{{item.description[:(100-len(item.title))]}}...
					</span>
				</a>
				<span class = "not-important">
					{{date_format(item.updated)}}
				</span>
			</span>

		</dt>
		<dd class = "description" data-id = "{{item.id}}" style = "display:none;">
		</dd>
		</div>		
		%end

		<div class="left">
		%if prev:
		  <a href = {{prev}} > Prev </a>
		%end
		%if next:
			<a href = {{next}} > Next </a>
		%end
		</div>
	</dl>
	<div style="display:none" id = "modal" class ="popup"></div>

</body>
</html>
<script>
	$(document).ready(function()
	{
		$('.title').click(function(event)
		{
			event.preventDefault();
			var title = $(this);
			console.log('loading content: ' + title.attr('href'));
			$.get(title.attr('href'), function(data) {
				$('dd[data-id="' + title.data('id') + '"]').html(data);
			});
			
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
				url: '{{request.script_name}}items/' + $(this).attr('data-id'),
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
			
		
		$('#subscribe').click(function(event){
			event.preventDefault();
			var l = $(this);
			l.addClass("active-modal");			
			$.get(l.attr('href'), function(data){
				$('#modal').html(data).show();
				$('#modal').css('top', l.offset().top + l.height());
				$('#modal').css('left', l.offset().left + l.width());
				$('input[name=url]').focus();
			});
		});
		
		$('#import').click(function(event){
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
		
		$('.external-link').mousedown(function(e) {			
			if (e.which <= 2) {
			e.preventDefault();			
			var item = $(this).parent().parent();
			item.addClass('read');					
			$.ajax({
				url: '{{request.script_name}}items/' + $(this).data('id'),
				data: '{"read" : true}',				
				contentType: "application/json; charset=utf-8",
				type: 'PATCH',
				error: function() {
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
