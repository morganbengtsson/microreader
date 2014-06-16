%from bottle import url
<link rel="stylesheet" type="text/css" href="{{url('/static/<filename:path>', filename='style.css')}}">

<form action="{{url('/channels/<id:int>/edit', id=channel.id)}}" method="POST">
			

<ol class = "horizontal nav-section">
	<li>
		<a href = "{{url('/channels/<id:int>/update', id=channel.id)}}" class= "update">
		<i class = "icon-arrow-circle"></i>
		Update
		</a>
	</li>	
	<li>
		<a href = "{{url('/channels/<id:int>/delete', id=channel.id)}}" class = "delete">
			<i class = "icon-cross"></i>
			Delete
		</a>
	</li>
</ol>
				
<ul>
<li>
	<label for = "title">Name</label> 
	<input type="text" name = "title" class="url" value="{{channel.title}}"/>
</li>
<li>
	<label for = "url">Url</label> 
	<input type="text" name = "url" class="url" value="{{channel.url}}"/>
</li>
<li>
	<button type="submit">Save</button>
</li>
</ul>
</form>
