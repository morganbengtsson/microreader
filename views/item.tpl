%from bottle import url
<h2>
<a class = "item-link" href = "{{item.url}}" target="_blank">
	{{item.title}}
</a>
</h2>
<span class="info">from <a href="{{url('/channels/<id:int>/items', id=item.channel.id)}}">{{item.channel.title}}</a> by {{item.author}}</span>
{{!item.description_html}}

