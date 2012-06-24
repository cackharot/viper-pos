/*
 *	Swizapp
 *	salesapp.js
 *	contains backbone based mvc app. for sales POS functionality
 */
(function ($) {

	LineItem = Backbone.Model.extend({
		defaults: {
			slno: null,
			productid: null,
			barcode: null,
			name: null,
			quantity: 0.0,
			mrp: 0.0,
			price: 0.0,
			discount: 0.0,
			subtotal: 0.0
		},
		initialize: function (model, options) {
			this.bind("change:name", this.updateUI)
			this.bind("change:quantity", this.updateUI)
			this.bind("change:mrp", this.updateUI)
			this.bind("change:price", this.updateUI)
			this.bind("change:barcode", this.updateUI)
		},
		updateUI: function () {
			var id = this.get('id')
			var barcode = this.get('barcode')
			var name = this.get('name')
			var quantity = this.get('quantity')
			var mrp = this.get('mrp')
			var price = this.get('price')
			var discount = this.get('discount')
			var subtotal = (price * quantity)

			this.set({'subtotal': subtotal})

			var $tr = $('tr[data-id=' + id + ']', $('#tblOrderLineItems tbody'))

			if ($tr.length > 0) {
				$('.n', $tr).text(name)
				$('.p', $tr).text(price)
				$('.d', $tr).text(discount)
				$('.q', $tr).text(quantity)
				$('.st', $tr).text(subtotal.toFixed(2))
			}
		}
	});

	LineItemCollection = Backbone.Collection.extend({
		model: LineItem,
		url: '/sales/savelineitems',
		initialize: function (models, options) {
			this.bind("add", this.addLineItemRecord)
			this.bind("change", this.updateTotal)
			this.bind("reset", this.resetRecords)
		},
		refreshUI: function (callback) {
			var that = this
			//$('#tblOrderLineItems tbody').hide()
			this.resetRecords()
			var cnt = 1
			this.each(function (item) {
				item.set({
					'slno': cnt++
				})
				that.addItemTpl(item)
			});
			this.updateTotal()
			//$('#tblOrderLineItems tbody').show()
		},
		addItemTpl: function (item) {
			var n = item.get('slno')
			if (!n) item.set({
				'slno': this.length
			})
			var compiled = _.template($('#tpl-lineitem').html())
			var tr = compiled({
				'item': item
			})
			$('#tblOrderLineItems tbody').prepend(tr)
		},
		addLineItemRecord: function (item) {
			this.addItemTpl(item)
			this.updateTotal()
		},
		updateTotal: function () {
			var qas = this.getQAS()
			$('#totalAmount').text(qas.totalAmount)
			$('#savingsAmount').text(qas.savings)
			$('#totalItemsQuantity').text(qas.totalItems + '/' + qas.totalQuantity)
		},
		getQAS: function () {
			var totalItems = 0,
				totalQuantity = 0,
				amt = 0,
				savings = 0;

			for (i = 0; i < this.length; i++) {
				var barcode = this.at(i).get('barcode')
				var price = this.at(i).get('price')
				var quantity = this.at(i).get('quantity')
				var mrp = this.at(i).get('mrp')
				var sbt = this.at(i).get('subtotal')

				if (!barcode.startsWith('.') && !barcode.startsWith('0.')) {
					totalQuantity += quantity
					totalItems++
				}

				amt += sbt
				savings += ((mrp * quantity) - sbt)
			}

			return {
				totalItems: totalItems,
				totalQuantity: totalQuantity,
				totalAmount: Math.round(amt),
				savings: Math.round(savings)
			}
		},
		resetRecords: function () {
			$('#tblOrderLineItems tbody tr').remove()
			$('#tblOrderLineItems tbody').html('<tr><td style="padding:0em;display: none;" class="noborder" colspan="7"></td></tr>')
			$('#totalAmount').text(0.0)
			$('#savingsAmount').text(0.0)
			$('#totalItemsQuantity').text('0/0')
		},
		hideUI: function (callback) {
			$('#tblOrderLineItems tbody').hide()
			if (callback) callback()
		},
		showUI: function (callback) {
			$('#tblOrderLineItems tbody').show()
			if (callback) callback()
		}
	});

	OrderPayment = Backbone.Model.extend({
		defaults: {
			id: null,
			orderid: null,
			paymentdate: new Date(),
			paymenttype: 'Cash',
			paidamount: 0.0,
			description: null
		}
	});

	OrderPaymentsCollection = Backbone.Collection.extend({
		model: OrderPayment,
	});

	Order = Backbone.Model.extend({
		urlRoot: '/sales/saveorder',
		defaults: {
			id: null,
			orderno: 0,
			orderdate: new Date(),
			duedate: null,
			customerid: null,
			customername: '',
			lineItems: new LineItemCollection,
			payments: new OrderPaymentsCollection,
			isprinted: false,
			ispaid: false,
			isdirty: false,
		},
		getOrderAmount: function () {
			return this.get('lineItems').reduce(function (m, x) {
				return m + x.get('subtotal');
			}, 0);
		},
		getPaidAmount: function () {
			return this.get('payments').reduce(function (m, x) {
				return m + x.get('paidamount');
			}, 0);
		}
	});

	OrdersCollection = Backbone.Collection.extend({});

	remote = (function () {
		var neworderurl = '/sales/neworder';
		var searchitemurl = '/sales/searchitem';
		return {
			newOrder: function (callback) {
				$.post(neworderurl, null, function (data) {
					if (callback) callback(data);
				}, 'json');
			},
			searchItem: function (barcode, callback) {
				$.post(searchitemurl, {'barcode': barcode }, function (data) {
					if (callback) callback(data);
				}, 'json');
			}
		};
	})();

	window.TodayOrderList = new OrdersCollection;

	window.OrderListView = Backbone.View.extend({
		el: $('#orderListDiv'),
		model: window.TodayOrderList,
		initialize: function (options) {
			this.vent = options.vent
			this.model = window.TodayOrderList

			_.bindAll(this, "updateorderitem")
			_.bindAll(this, "loadTodayOrders")

			this.model.bind('add', this.addorderitem)
			this.model.bind('remove', this.removeorderitem)
			this.vent.bind("updateOrder", this.updateorderitem)
			this.vent.bind("resetUI", this.resetUI)
			this.vent.bind("loadTodayOrders", this.loadTodayOrders)

			this.loadTodayOrders()
		},
		events: {
			"click #tblTodayOrders tbody tr": "editOrder"
		},
		editOrder: function (e) {
			$('#tblTodayOrders tbody').find('.active').removeClass('active')
			var $tr = $(e.target).parent()
			$tr.addClass('active')
			var orderid = $tr.data('orderid')
			this.vent.trigger('editOrder', orderid)
		},
		addorderitem: function (item) {
			if (!item) return;
			var compiled = _.template($('#tpl-todayorderitem').html());
			var $tr = $(compiled({
				'item': item
			}));
			$('#tblTodayOrders tbody').prepend($tr)

			if (item.get('isNew')) {
				item.set({
					'isNew': false
				})
				$('#tblTodayOrders tbody').find('.active').removeClass('active')
				$tr.addClass('active')
			}
		},
		removeorderitem: function (item) {
			if (!item) return
			var orderid = item.get('orderid')
			var $tr = $('tr[data-orderid=' + orderid + ']', $('#tblTodayOrders tbody'))
			if ($tr.length > 0) $tr.remove()
		},
		updateorderitem: function (orderid) {
			if (!orderid) return
			var item = this.model.find(function (x) {
				return x.get('orderid') == orderid
			});
			if (item) {
				var orderno = item.get('orderno')
				var odate = item.get('orderdate')
				var amt = item.getOrderAmount()

				item.set({
					'orderamount': amt
				})
				
				var $tr = $('#tblTodayOrders tbody tr[data-orderid='+orderid+']')
				
				if(item.get('isdirty')) {
					if(!$tr.hasClass('dirty'))
						$tr.addClass('dirty')
				}else if($tr.hasClass('dirty')){
					$tr.removeClass('dirty')
				}

				var $tr = $('tr[data-orderid="' + orderid + '"]', $('#tblTodayOrders tbody'))
				if ($tr.length > 0) {
					$('.o', $tr).text(orderno)
					$('.c', $tr).text(ToLocalDate(odate))
					$('.a', $tr).text(Math.round(amt))
				}
			}
		},
		resetUI: function () {
			$('#tblTodayOrders tbody tr').remove()
		},
		loadTodayOrders: function () {
			this.resetUI()
			$('#tblTodayOrders tbody').hide()
			var model = this.model
			model.reset()
			$.ajax({
				url: '/sales/todayorders',
				accepts: 'application/json',
				contentType: 'application/json',
				data: null,
				dataType: 'json',
				type: 'POST'
			}).done(function (data, textStatus, xhr) {
				if (data && data.length > 0) {
					for (var item = data.length - 1; item >= 0; --item) {
						if (data[item] && data[item].Id) {
							var o = new Order;
							o.set({
								'orderid': data[item].Id,
								'customerid': data[item].CustomerId,
								'customername': data[item].CustomerName,
								'orderno': data[item].OrderNo,
								'orderdate': data[item].OrderDate,
								'duedate': data[item].DueDate,
								'paidamount': data[item].PaidAmount,
								'orderamount': data[item].OrderAmount,
								'lineItems': new LineItemCollection,
								'payments': new OrderPaymentsCollection,
								'isprinted': false,
								'isloaded': false,
								'ispaid': data[item].PaidAmount > 0,
								'isNew': false,
							});
							model.add(o)
						}
					}
				} else {
					showMsg('warn', '<strong>Hmmm!</strong> No orders made today.', false)
				}
				$('#tblTodayOrders tbody').show()
			}).fail(function () {
				showMsg('warn', '<strong>Oops!</strong> Error in loading todays order details.', false)
				$('#tblTodayOrders tbody').show()
			})
		}
	});

	window.SalesAppView = Backbone.View.extend({
		el: $("#invoice-container"),
		model: null,
		initialize: function (options) {
			this.vent = options.vent
			this.lstOrders = window.TodayOrderList

			_.bindAll(this, "editOrder")
			_.bindAll(this, "payOrder")
			_.bindAll(this, "updateLineItem")
			_.bindAll(this, "updateInvoiceCustomer")
			_.bindAll(this, "updateDuedate")

			this.vent.bind('editOrder', this.editOrder)
			this.vent.bind('updateLineItem', this.updateLineItem)
			this.vent.bind('updateDuedate', this.updateDuedate)
			
			this.itemNameTypeahead()
			this.customerNameTypeahead()
		},
		render: function () {
			//console.log('updating order')
			var item = this.model
			var odate = $.format.date(ToLocalDate(item.get('orderdate')), 'dd-MM-yyyy hh:mm a')
			
			if(item.get('duedate')) {
				var duedate = item.get('duedate')
			 	duedate = $.format.date(ToLocalDate(duedate), 'dd-MM-yyyy')
				$('#dueDate').val(duedate)
			}else{
				$('#dueDate').val('')
			}
			
			$('#orderDate').html(odate)
			$('#orderNumber').html(item.get('orderno'))
			$('#invoiceCustomerName').text(item.get('customername').toUpperCase() || '')
			this.updateAmounts()
		},
		updateAmounts: function () {
			var pamt = Math.round(this.model.get('paidamount'))
			var tamt = Math.round(this.model.get('orderamount'))
			
			$('#paymentType').text((tamt>pamt ? 'Credit':'Cash'))
			$('#paymentType').attr('class',tamt>pamt ? 'status opened':'status closed')
			
			if (pamt > 0) {
				var balance = (tamt - pamt)
				$('#paidAmount').text(pamt)
				$('#balanceAmount').text(balance)
			} else {
				$('#paidAmount').text(0.0)
				$('#balanceAmount').text(0.0)
			}
		},
		resetOrder: function(){
			if(this.model) {
				this.model.get('lineItems').reset()
				this.model.unbind('change',this.render)
				this.model = null
			}
			
			$('#orderDate').html('')
			$('#dueDate').val('')
			$('#orderNumber').html('')
			
			$('#paidAmount').text(0.0)
			$('#balanceAmount').text(0.0)
			
			$('#paymentType').text('')
			$('#paymentType').attr('class','')
		},
		events: {
			"click #add-item": "addLineItem",
			"click #delete-item": "deleteLineItem",
			"click #print-order": "printOrder",
			"click #preview-order": "previewOrder",
			"click #new-order": "newOrderClick",
			"click #cancel-order": "cancelOrder",
			"click #checkout-order": "checkOutOrder",
			"click a.del-lineitem": "deleteLineItem",
			"click #refresh-orders": "refreshOrders",
			"click #save-order": "saveOrder",
			"keyup input[name=barcode]": "key_addlineitem",
			"keyup input[name=itemName]": "key_addlineitem",
		},
		saveOrder: function() {
			if(this.model && this.model.get('lineItems').length > 0) {
				this.model.save()
				showMsg('success', '#'+ this.model.get('orderno') + ' - Invoice saved successfully!')
			}else{
				showMsg('warn','No Items added to the invoice. Cannot save invoice!')
			}
		},
		refreshOrders: function(){
			this.resetOrder()
			this.vent.trigger("loadTodayOrders")
		},
		key_addlineitem: function (e) {
			if (e.keyCode == 13) 
				this.addLineItem()
		},
		updateDuedate: function(duedate){
			if(this.model && duedate) {
				this.model.set('duedate', duedate)
			}
		},
		updateLineItem: function(data){
			if(!this.model || !data)
				return
			var item = this.model.get('lineItems').find(function(x){
				return x.get('id') == data.id
			})
			if(item) {
				item.set(data.col, data.value)
				this.updateAmounts()
			}
		},
		deleteLineItem: function (e) {
			e.preventDefault()
			var slno = $(e.target).data('slno')
			//console.log(slno)
			if (slno) {
				var items = this.model.get('lineItems')
				var item = items.find(function (x) {
					return x.get('slno') == slno;
				})
				if (item) {
					items.remove(item)
					items.refreshUI()
					this.vent.trigger('updateOrder', this.model.get('orderid'))
					showMsg('warn', '<span class="label label-info">' + item.get('name') + '</span> removed from the order!')
				}
			}
		},
		itemNameTypeahead: function () {
			var that = this
			$('input[name=itemName]').typeahead({
				idField: 'Barcode',
				idControl: $('input[name=barcode]'),
				onSelected: function (item) {
					if (!that.model) {
						showMsg('warn', 'Please click new order to add items!')
						return
					}
					var tmp = $('input[name=quantity]').val();
					var quantity = 1.0;
					if (tmp && tmp.length > 0) quantity = parseFloat(tmp);
					var found = that.findAndUpdateItem(item.Barcode, quantity)
					if (!found) {
						item.Quantity = 1;
						that.addItemToUI(item, that);
					}
					$('#itemName').focus()
				},
				formatter: function (displayValue, item) {
					return '<div style="width:220px;display:block;height:21px;"><span style="float:left;">' + displayValue + '</span><span style="float:right;margin-left:15px;font-style:italic">' + item.MRP.toFixed(2) + '</span></div>';
				},
				ajax: {
					url: "/sales/searchitem",
					timeout: 500,
					displayField: "Name",
					triggerLength: 1,
					method: 'post',
					dataType: 'json',
					loadingClass: "loading-circle icon-refresh",
					preDispatch: function (query) {
						return {
							name: query,
						}
					},
					preProcess: function (data) {
						if (!data) return false
						if (data.success === false)	return false
						return data
					}
				}
			});
		},
		updateInvoiceCustomer: function (item) {
			if(!this.model) {
				showMsg('warn','Please create new invoice!')
				return
			}
			var cusname = $('#customerName').val().trim()
			var cusid = $('#customerid').val().trim()
			if(cusname && cusid) {
				this.model.set({
						'customername':cusname,
						'customerid':cusid
				})
			}
		},
		customerNameTypeahead: function(){
			$('#customerName').typeahead({
				idField: 'id',
				idControl: $('#customerid'),
				onSelected: this.updateInvoiceCustomer,
				formatter: function (displayValue, item) {
					var fieldName = $('input[type=radio][name=searchfield]:checked').val()
					if (fieldName != 'name')
						return '<div style="width:100%;display:block;height:21px;"><span style="float:left;">' + displayValue + '</span><span style="float:right;margin-left:15px;font-style:italic">' + item.name + '</span></div>';
					else
						return '<div style="width:100%;display:block;height:21px;"><span style="float:left;">' + displayValue + '</span><span style="float:right;margin-left:15px;font-style:italic">' + item.mobile + '</span></div>';
				},
				ajax: {
					url: "/customers/search",
					timeout: 500,
					displayField: "name",
					triggerLength: 1,
					method: 'post',
					dataType: 'json',
					loadingClass: "loading-circle icon-refresh",
					preDispatch: function (query) {
						//showLoadingMask(true);
						var fieldName = $('input[type=radio][name=searchfield]:checked').val()
						this.displayField = fieldName
						return {
							search: query,
							field: fieldName || 'name'
						}
					},
					preProcess: function (data) {
						//showLoadingMask(false);
						if (!data || !data.mylist) return false
						if (data.success === false) return false
						return data.mylist
					}
				}
			})
		},
		findAndUpdateItem: function (barcode, quantity) {
			var item = this.model.get('lineItems').find(function (x) {
				return x.get('barcode') == barcode
			})
			if (item) {
				var q = item.get('quantity')
				item.set({
					'quantity': q + quantity
				})
				$('input[name=itemName]').val(item.get('name'))
				this.model.set({'isdirty': true})
				this.vent.trigger('updateOrder', this.model.get('orderid'))
				return true
			}
			return false
		},
		addLineItem: function () {
			var $txtBarcode = $('input[name=barcode]')
			var barcode = $txtBarcode.val()
			
			if (!this.model && barcode && barcode.length > 0) {
				this.newOrder(function () {
					$('#add-item').trigger('click')
				})
				return
			}
			
			var tmp = $('input[name=quantity]').val()
			var quantity = 1.0
			if (tmp && tmp.length > 0) quantity = parseFloat(tmp)

			if (barcode && barcode.length > 0 && barcode.length < 20 && quantity > 0) {
				var found = this.findAndUpdateItem(barcode, quantity)
				if (!found) {
					var that = this

					remote.searchItem(barcode, function (data) {
						if (data) {
							if (data.length > 1) {
								var compl = _.template($('#tpl-selectitem').html())
								var tr = compl({'items': data})
								$('#tblSelectItem tbody').html(tr)

								$('#tblSelectItem tbody td button').each(function () {
									$(this).click(function () {
										var id = parseInt($(this).data('id'))
										data[id].Quantity = quantity
										that.addItemToUI(data[id], that)

										$('#tblSelectItem tbody').html('')
										$('#selectItemModal').modal('hide')
										$('input[name=itemName]').val(data[id].Name)
										$('#barcode').focus()
									});
								});

								// show pop to select the item
								$('#selectItemModal').modal('show')
							} else {
								data[0].Quantity = quantity
								that.addItemToUI(data[0], that)
								$('input[name=itemName]').val(data[0].Name)
								$('#barcode').focus()
							}
						} else {
							if (!isNaN(barcode)) {
								var mrp = parseFloat(barcode)
								if (mrp <= 1000.00) {
									var d = {}
									d.Barcode = mrp.toString()
									d.MRP = mrp
									d.SellPrice = mrp
									d.Quantity = 1.0
									d.Name = ''
									d.Discount = 0.0
									d.Id = null
									that.addItemToUI(d, that)
								} else {
									showMsg('warn', '<strong>Oops!</strong> There are no items with barcode <span class="label label-info">' + barcode + '</span>.')
								}
							} else {
								showMsg('warn', '<strong>Oops!</strong> There are no items with barcode <span class="label label-info">' + barcode + '</span>.')
							}

							$('#barcode').focus()
						}
					});
				} else {
					$('#barcode').focus()
				}
			} else {
				showMsg('warn', '<strong>Enter a valid barcode!</strong>')
				$('#barcode').focus()
			}
		},
		addItemToUI: function (data, that) {
			var barcode = data.Barcode
			var itemName = data.Name
			var price = data.SellPrice
			var discount = data.Discount
			var mrp = data.MRP
			var quantity = data.Quantity

			var item = new LineItem({
				id: uuid(),
				orderid: that.model.get('orderid'),
				productid: data.Id,
				name: itemName,
				barcode: barcode,
				mrp: mrp,
				quantity: quantity,
				price: price,
				discount: discount,
				subtotal: (price * quantity)
			});

			item.hasMultiple = data.hasMultiple
			that.model.set({'isdirty': true})
			that.model.get('lineItems').add(item)
			that.vent.trigger('updateOrder', that.model.get('orderid'))
		},
		newOrderClick: function (e) {
			this.newOrder(function () {
				$('#barcode').focus()
			})
		},
		newOrder: function (callback) {
			if (this.model) {
				this.model.unbind("change", this.render)
				var items = this.model.get('lineItems')
				items.resetRecords()
			}

			this.model = new Order
			this.bindOrder()
			this.model.get('lineItems').reset()
			this.model.get('payments').reset()

			var lstorders = this.lstOrders
			var currentOrder = this.model

			remote.newOrder(function (data) {
				if (data) {
					currentOrder.set({
						'id': data.Id,
						'orderid': data.Id,
						'customerid': data.CustomerId,
						'customername': data.CustomerName,
						'orderno': data.OrderNo,
						'orderdate': data.OrderDate,
						'duedate': null,
						'paidamount': data.PaidAmount,
						'orderamount': data.OrderAmount,
						'isNew': true,
						'isdirty':false,
					})
					lstorders.add(currentOrder)
					hideMsg()
					if (callback) callback()
				}else{
					showMsg('error','Oops! Error creating new invoice!');
				}
			});
		},
		bindOrder: function(){
			/*this.model.bind("change:customerid", this.render, this)
			this.model.bind("change:customername", this.render, this)
			this.model.bind("change:orderamount", this.render, this)
			this.model.bind("change:paidamount", this.render, this)
			this.model.bind("change:balanceamount", this.render, this)
			this.model.bind("change:isdirty", this.render, this)*/
			this.model.bind("change", this.render, this)
		},
		editOrder: function (orderid) {
			if (!orderid || (this.model && orderid == this.model.get('orderid'))) return

			found = this.lstOrders.find(function (x) {
				return x.get('orderid') == orderid
			})

			if (found) {
				if(this.model) this.model.unbind("change", this.render)
				this.model = found
				this.bindOrder()
				
				if (!found.get('isloaded') === true) {
					this.fetchAndEditOrder(orderid)
				} else {
					this.model.get('lineItems').refreshUI()
					this.render()
					$('#barcode').focus()
				}
			} else {
				showMsg('error', '<strong>Oops!</strong> Something went really wrong.')
			}
		},
		fetchAndEditOrder: function (orderid) {
			var currentOrder = this.model
			var items = this.model.get('lineItems')
			//items.hideUI()
			
			$.post('/sales/getorder/' + orderid, null, function (data) {
				if (data) {
					var o = data.order
					var orderid = o.Id
					var lineitems = data.lineitems
					var payments = data.payments

					currentOrder.set({
						'id': o.Id,
						'orderid': o.Id,
						'customerid': o.CustomerId,
						'customername': o.CustomerName,
						'orderno': o.OrderNo,
						'orderdate': o.OrderDate,
						'duedate': o.DueDate,
						'paidamount': o.PaidAmount,
						'orderamount': o.OrderAmount,
						'isloaded': true,
					})

					if (lineitems) {
						for (var i = 0; i < lineitems.length; i++) {
							var price = lineitems[i].SellPrice
							var quantity = lineitems[i].Quantity
							var item = new LineItem({
								id: uuid(),
								productid: lineitems[i].ProductId,
								name: lineitems[i].Name,
								barcode: lineitems[i].Barcode,
								mrp: lineitems[i].MRP,
								quantity: quantity,
								price: price,
								discount: lineitems[i].Discount,
								subtotal: (price * quantity)
							})
							currentOrder.get('lineItems').add(item)
						}
					}

					if (payments) {
						for (var i = 0; i < payments.length; i++) {
							var no = i + 1
							var item = new OrderPayment({
								slno: no,
								orderid: orderid,
								paidamount: payments[i].PaidAmount,
								paymenttype: payments[i].PaymentType,
								paymentdate: payments[i].PaymentDate,
							})
							currentOrder.get('payments').add(item)
						}
					}

					currentOrder.set({
						'paidamount': currentOrder.getPaidAmount(),
						'orderamount': currentOrder.getOrderAmount(),
					})

					items.refreshUI()
					
					$('#barcode').focus()
				}
			});
		},
		cancelOrder: function () {
			if (this.model) {
				this.model.get('lineItems').reset()
				this.model.get('payments').reset()
				this.vent.trigger('updateOrder', this.model.get('orderid'))
				this.render()
				$('#barcode').focus()
			}
		},
		checkOutOrder: function () {
			if (!this.model || this.model.get('lineItems').length < 1) {
				showMsg('warn', '<strong>Oops!</strong> Order contains no items. Cannot <span class="label label-info">checkout</span>.', false)
				return
			}
			
			if (!this.model.get('customerid')) {
				showMsg('error', '<strong>Oops!</strong> Please enter a valid customer to save this order.')
				return
			}

			var orderamt = this.model.get('orderamount')
			var paidamt = this.model.getPaidAmount()
			var balanceamt = paidamt > orderamt ? 0.0 : (orderamt - paidamt)
			
			this.model.set({'balanceamount': balanceamt})

			var cmpl = _.template($('#tpl-chkoutorder').html())
			var html = cmpl({
				'item': this.model
			})
			$('#checkoutOrderModel .modal-body').html(html)

			$('#checkoutOrderModel').modal('show')

			$('#btnPayOrder', $('#checkoutOrderModel')).focus()
			$('#btnPayOrder', $('#checkoutOrderModel')).unbind('click', this.payOrder)
			$('#btnPayOrder', $('#checkoutOrderModel')).click(this.payOrder)
		},
		payOrder: function () {
			var orderid = this.model.get('orderid')
			var paidamount = Math.round(parseFloat($('input[name=paidamount]', $('#checkoutOrderModel')).val()))
			var paymenttype = $('select[name=paymenttype] option:selected', $('#checkoutOrderModel')).val()
			var canprint = $('input[name=printTicket]', $('#checkoutOrderModel')).is(':checked')
			var oa = this.model.getOrderAmount()
			var pa = this.model.getPaidAmount()
			var orderamount = Math.round(oa)
			var prevpaidamt = Math.round(pa)

			if ((paymenttype == 'Cash' && (prevpaidamt + paidamount >= orderamount)) || (paymenttype == 'Credit' && paidamount < orderamount) || (paymenttype == 'Card' && paidamount > 0.0) || (paymenttype == 'Cheque' && paidamount > 0.0)) {
				
				if(oa > orderamount) {
					paidamount += (oa-orderamount);//round off the less than 0.5 paise
				}
				
				this.model.set({
					'paidamount': prevpaidamt + paidamount,
					'isloaded': true,
					'isdirty': false,
				})

				var payment = new OrderPayment({
					'orderid': orderid,
					'paidamount': paidamount,
					'paymenttype': paymenttype,
					'paymentdate': new Date().toUTCString(),
				})

				this.model.get('payments').add(payment)
				this.model.save()
				showMsg('success', '<strong>Hooray!</strong> Payment Successfull &amp; <strong>#'+this.model.get('orderno')+'</strong> Invoice is saved.')
				
				this.vent.trigger('updateOrder', orderid)
				
				if(canprint)
					this.printOrder()
			} else if (paymenttype == 'Credit' && paidamount >= orderamount) {
				showMsg('warn', '<strong>Oops!</strong> Wrong Payment Type. Please choose <span class="label label-info">Cash</span> as payment type if the paid amount is greater than order amount.')
			} else {
				showMsg('warn', 'Paid amount should be greater than or equal to <strong>' + orderamount + '</strong>. Please choose <span class="label label-info">Credit</span> as payment type if the paid amount is lesser than order amount.')
			}
			
			$(this).unbind('click', this.payOrder)
			$('#checkoutOrderModel').modal('hide')
		},
		printOrder: function () {
			this.showPrintableOrder(function (w) {
				w.print()
				w.close()
			});
		},
		previewOrder: function (e, callback) {
			this.showPrintableOrder()
		},
		showPrintableOrder: function (callback) {
			if (!this.model || this.model.get('lineItems').length <= 0) {
				showMsg('warn', 'No active order! Cannot print!')
				return;
			}
			var that = this
			templateLoader.loadRemoteTemplate("tplPrintOrder", "/static/templates/printorder.html", function (data) {
				var compiled = _.template(data)
				var pw = window.open('', 'PrintOrder', 'width=400,height=600,resizeable,scrollbars')
				pw.document.write(compiled({
					order: that.model
				}))
				pw.document.close()
				if (callback) callback(pw)
			});
		}
	});

	var vent = _.extend({}, Backbone.Events)
	var salesappview = new SalesAppView({
		vent: vent
	})
	var orderlistview = new OrderListView({
		vent: vent
	})

	templateLoader.clearLocalStorage();
	
	$('#dueDate').blur(function(){
		var tmp = $(this).val()
		if(tmp && tmp.length>1){
			try{
				var duedate = $.datepicker.parseDate('dd-mm-yy', tmp);
				vent.trigger('updateDuedate', duedate)
			}catch(e){
				showMsg('error',e)
			}
		}		
	})
	
	$('#hiddenDuedateSelect').datepicker({
			dateFormat:'yy-mm-dd',
			showAnim: 'slide',
			changeMonth: true,
			changeYear: true,
			onSelect: function( selectedDate ) {
				vent.trigger('updateDuedate', selectedDate)
			}
	})
	
	$('table#tblOrderLineItems tbody td.edit').live('click', function(){
		var w = $(this).width()-10
		$(this).editable(function(value,settings){
			var col = $(this).data('col')
			var id = $(this).parent().data('id')
			var val = null
			if(col != 'name') {
				val = !isNaN(value) ? parseFloat(value) : null
				value = val
			}else{
				val = value
			}
			if(val) {
				vent.trigger('updateLineItem',{id:id, col:col, value:val})
				return value
			}
		},
		{
			event: 'edit',
			height: 20,
			width: w,
			cssclass: 'inline-form',
		})
		$(this).trigger('edit')
	})

	String.prototype.startsWith = function (needle) {
		return (this.indexOf(needle) == 0);
	};

	uuid = function () {
		// Otherwise, just use Math.random
		// http://stackoverflow.com/questions/105034/how-to-create-a-guid-uuid-in-javascript/2117523#2117523
		return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
			var r = Math.random() * 16 | 0,
				v = c == 'x' ? r : (r & 0x3 | 0x8);
			return v.toString(16);
		});
	};

	function listen(e) {
		//console.log(e.type)
		//console.log(e.keyCode)
		var isHandled = false;
		switch (e.keyCode) {
		case 114:
			//F3
			//new order
			isHandled = true
			$('#new-order').trigger('click');
			break;
		case 115:
			//F4
			//cancel order
			isHandled = true
			$('#cancel-order').trigger('click');
			break;
		case 116:
			//F5
			//checkout order
			isHandled = true
			$('#checkout-order').trigger('click');
			break;
		case 117:
			// focus barcode
			isHandled = true
			$('#barcode').focus();
			break;
		case 122:
			//print order
			isHandled = true
			$('#print-order').trigger('click');
			break;
		case 123:
			//preview order
			isHandled = true
			$('#preview-order').trigger('click');
			break;
		}
		if (isHandled) e.preventDefault()
	}

	$(document).bind('keypress', listen)
	//$(document).bind('keyup', listen);
})(jQuery);
