$.fn.serializeObject = function()
{
	var o = {};
	var a = this.serializeArray();
	$.each(a, function() {
	    if (o[this.name] !== undefined) {
	        if (!o[this.name].push) {
	            o[this.name] = [o[this.name]];
	        }
	        o[this.name].push(this.value || '');
	    } else {
	        o[this.name] = this.value || '';
	    }
	});
	return o;
};

function ToLocalDate(inDate) {
	if (_.isString(inDate)) inDate = new Date(inDate);
	var date = new Date();
	date.setTime(inDate.valueOf() - 60000 * inDate.getTimezoneOffset());
	return date;
}
		
function hideMsg() {
	$('#statusMessage').fadeOut();
}

function showMsg(type, message, timeout) {
	$(document).trigger('NotificationEvent',
	{
		type: type,
		message: message
	});
}

// Apply to TR elements only
$.fn.rowClick = function(f){
    var options = $.extend({
      preventOn: 'a, button, input'
    }, arguments[1]||{});
    var tr = $(this).filter('tr');
    tr.click(f).find(options.preventOn).click(function(e){
    	//console.log(e.target) 
    	e.stopPropagation();
    	//e.preventDefault() 
    });
    return $(this);
};

$(function() {
	var showMsg = showMsg;
	var hideMsg = hideMsg;
	
	$(window).bind("unload", function() {$('button,a').die('click');});
	
	$(document).bind('AjaxRefreshEvent',function(e,data){
		if(window.swizapp.urls.edit)
		{
			var tr = $('table.listing:not(".noedit") tbody tr:not(".payments-row")');
			
			tr.rowClick(function() {
				var id = $(this).data('id');
				if (id)
		 			window.location.href =	window.swizapp.urls.edit + id;
			});
		}
	});
	$(document).trigger('AjaxRefreshEvent');
});

// ---------- SwizappFormTips------------------------------
/*
Adds a label tag with a 'tip' class before any element with an id and a title attributes and,
if wrapper tag provided, wraps both into a relative positioned tag. If not, their parent tag
is positioned relative. You can set not to position parent if you want. You can also change
default tip class name.

Options & defaults:
- wrapper   : null  (no wrapper)
- relative  : true  (parent will be positioned as 'relative')
- classname : 'tip' (label class name)
- test      : false (if true, sets a title for all items to test behavior)
- is_new    : false (if true, the form is not for editing db object)

<carlos@markhaus.com>
*/
$.fn.SwizappFormTips = function (options) {
	var parent, options = $.extend({
		wrapper: null,
		relative: true,
		classname: 'tip',
		test: false,
		is_new: false
	}, options || {});

	if (options.test) {
		this.attr('title', 'Lorem ipsum et dolor sit amet');
	}

	return this.each(function (i) {
		if (this.id && this.title) {
			if (options.wrapper) {
				parent = $(this).wrap('<' + options.wrapper.toLowerCase() + '></' + options.wrapper.toLowerCase() + '>').parent();
			} else {
				parent = $(this).parent();
			}

			if (options.relative) {
				parent.css('position', 'relative');
			}

			var label = $('<label id="' + this.id + '_label" for="' + this.id + '" class="tip" style="display:none;">' + this.title + '</label>');
			label.css({
				left: '0px',
				top: $(this).height() + 'px'
			});
			$(this).before(label);

			$(this).bind('focus', function (e) {
				//$(this).select(); // select text (to work also in textareas)
				$('#' + this.id + '_label').fadeIn('fast');
				if (options.is_new && $(this).val() == this.title) {
					$(this).val('');
				}
			}).bind('blur', function (e) {
				//$(this).val($(this).val()); // Unselect text (the same as before)
				$('#' + this.id + '_label').fadeOut('fast');
			});
		}
	});
};
