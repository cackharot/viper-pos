/*
 *	Viper POS
 *	salesapp.js
 *	contains backbone based mvc app.
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
			this.bind("change:name", this.updateUI);
			this.bind("change:quantity", this.updateUI);
			this.bind("change:mrp", this.updateUI);
			this.bind("change:price", this.updateUI);
			this.bind("change:barcode", this.updateUI);
		},
		updateUI: function () {
			var id = this.get('id');
			var barcode = this.get('barcode');
			var name = this.get('name');
			var quantity = this.get('quantity');
			var mrp = this.get('mrp');
			var price = this.get('price');
			var discount = this.get('discount');
			var subtotal = Math.round(price * quantity);

			this.set({
				'subtotal': subtotal
			})

			var $tr = $('tr[data-id=' + id + ']', $('#tblOrderLineItems tbody'));

			if ($tr.length > 0) {
				$('.n', $tr).text(name);
				$('.p', $tr).text(price);
				$('.d', $tr).text(discount);
				$('.q', $tr).text(quantity);
				$('.st', $tr).text(subtotal);
			}
		}
	});

	LineItemCollection = Backbone.Collection.extend({
		model: LineItem,
		url: '/sales/savelineitems',
		initialize: function (models, options) {
			this.bind("add", this.addLineItemRecord);
			this.bind("change", this.updateTotal);
			this.bind("reset", this.resetRecords);
		},
		refreshUI: function (callback) {
			var that = this
			this.hideUI(function () {
				that.resetRecords();
				var cnt = 1;
				that.each(function (item) {
					item.set({
						'slno': cnt++
					})
					that.addItemTpl(item)
				});
				that.updateTotal();
				that.showUI(function () {
					if (callback) callback();
				});
			});
		},
		addItemTpl: function (item) {
			var n = item.get('slno')
			if (!n) item.set({
				'slno': this.length
			})
			var compiled = _.template($('#tpl-lineitem').html());
			var tr = compiled({
				'item': item
			});
			$('#tblOrderLineItems tbody').prepend(tr);
		},
		addLineItemRecord: function (item) {
			this.addItemTpl(item);
			this.updateTotal();
		},
		updateTotal: function () {
			var qas = this.getQAS();
			$('#totalAmount').text(qas.totalAmount);
			$('#savingsAmount').text(qas.savings);
			$('#totalItemsQuantity').text(qas.totalItems + '/' + qas.totalQuantity);
		},
		getQAS: function () {
			var totalItems = 0,
				totalQuantity = 0,
				amt = 0,
				savings = 0;

			for (i = 0; i < this.length; i++) {
				var barcode = this.at(i).get('barcode');
				var price = this.at(i).get('price');
				var quantity = this.at(i).get('quantity');
				var mrp = this.at(i).get('mrp');
				var sbt = this.at(i).get('subtotal');

				if (!barcode.startsWith('.') && !barcode.startsWith('0.')) {
					totalQuantity += quantity;
					totalItems++;
				}

				amt += sbt;
				savings += ((mrp * quantity) - sbt);
			}

			totalQuantity = totalQuantity.toFixed(2);
			amt = Math.round(amt);
			savings = Math.round(savings);
			return {
				totalItems: totalItems,
				totalQuantity: totalQuantity,
				totalAmount: amt,
				savings: savings
			};
		},
		resetRecords: function () {
			$('#tblOrderLineItems tbody tr').each(function () {
				$(this).remove();
			});
			$('#totalAmount').text(0.0);
			$('#savingsAmount').text(0.0);
			$('#totalItemsQuantity').text('0/0');
		},
		hideUI: function (callback) {
			$('#tblOrderLineItems tbody').fadeOut('normal', function (e) {
				if (callback) callback();
			});
		},
		showUI: function (callback) {
			$('#tblOrderLineItems tbody').fadeIn('false', function (e) {
				if (callback) callback();
			});
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
			customerid: null,
			customername: '',
			lineItems: new LineItemCollection,
			payments: new OrderPaymentsCollection,
			isprinted: false,
			ispaid: false,
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
				var order = {};
				$.post(neworderurl, null, function (data) {
					if (typeof (data) == "string") data = eval('(' + data + ')');
					order = data;
					if (callback) callback(data);
				}, 'json');
				return order;
			},
			searchItem: function (barcode, callback) {
				$.post(searchitemurl, {
					'barcode': barcode
				}, function (data) {
					if (typeof (data) == "string") data = eval('(' + data + ')');
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

			this.model.bind('add', this.addorderitem)
			this.model.bind('remove', this.removeorderitem)
			this.vent.bind("updateOrder", this.updateorderitem)
			this.vent.bind("resetUI", this.resetUI)
			this.vent.bind("loadTodayOrders", this.loadTodayOrders)

			this.loadTodayOrders()
		},
		events: {
			"click #refresh-orders": "loadTodayOrders",
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
			if (!item) return;
			var orderid = item.get('orderid');
			var $tr = $('tr[data-orderid=' + orderid + ']', $('#tblTodayOrders tbody'));
			if ($tr.length > 0) $tr.remove();
		},
		updateorderitem: function (orderid) {
			if (!orderid) return;
			var item = this.model.find(function (x) {
				return x.get('orderid') == orderid;
			});
			if (item) {
				var orderno = item.get('orderno');
				var odate = item.get('orderdate');
				var amt = item.getOrderAmount();

				item.set({
					'orderamount': amt
				})

				var $tr = $('tr[data-orderid="' + orderid + '"]', $('#tblTodayOrders tbody'));
				if ($tr.length > 0) {
					$('.o', $tr).text(orderno);
					$('.c', $tr).text(ToLocalDate(odate));
					$('.a', $tr).text(amt.toFixed(2));
				}
			}
		},
		resetUI: function () {
			$('#tblTodayOrders tbody tr').each(function () {
				$(this).remove();
			});
		},
		loadTodayOrders: function () {
			this.resetUI()
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
				if (typeof (data) == "string") data = eval('(' + data + ')');
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
					};
				} else {
					showMsg('info', '<strong>Hmmm!</strong> No orders made today.', false);
				}
			}).fail(function () {
				showMsg('warn', '<strong>Oops!</strong> Error in loading todays order details.', false);
			});
		}
	});

	window.SalesAppView = Backbone.View.extend({
		el: $("#sales-page"),
		model: null,
		initialize: function (options) {
			this.vent = options.vent
			this.lstOrders = window.TodayOrderList

			_.bindAll(this, "editOrder");
			_.bindAll(this, "updateLineItem");

			this.vent.bind('editOrder', this.editOrder)
			this.vent.bind('updateLineItem', this.updateLineItem)
			this.itemNameTypeahead()
		},
		render: function () {
			//console.log('updating order')
			var item = this.model
			var odate = $.format.date(ToLocalDate(item.get('orderdate')), 'dd-MM-yyyy hh:mm a')

			$('#orderDate').html(odate)
			$('#orderNumber').html(item.get('orderno'))
			$('#customerName').text(item.get('customername') || '')
			this.updateAmounts()
		},
		updateAmounts: function () {
			var pamt = this.model.getPaidAmount()
			var tamt = this.model.getOrderAmount()
			if (this.model.get('ispaid') === true || pamt > 0) {
				var balance = tamt - pamt
				$('#paidAmount').text(pamt)
				$('#balanceAmount').text(balance)
			} else {
				$('#paidAmount').text(0.0)
				$('#balanceAmount').text(0.0)
			}
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
			"keyup input[name=barcode]": "key_addlineitem",
			"keyup input[name=itemName]": "key_addlineitem",
		},
		key_addlineitem: function (e) {
			if (e.keyCode == 13) this.addLineItem();
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
			var slno = $(e.target).parent().data('slno')
			if (slno) {
				var items = this.model.get('lineItems')
				var item = items.find(function (x) {
					return x.get('slno') == slno;
				})
				if (item) {
					items.remove(item)
					items.refreshUI()
					this.vent.trigger('updateOrder', this.model.get('orderid'))
					showMsg('info', '<span class="label label-info">' + item.get('name') + '</span> removed from the order!')
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
					$('input[name=itemName]')[0].select(0, $('input[name=itemName]').val().length);
				},
				formatter: function (displayValue, item) {
					return '<div style="width:100%;display:block;height:21px;"><span style="float:left;">' + displayValue + '</span><span style="float:right;margin-left:15px;font-style:italic">' + item.MRP.toFixed(2) + '</span></div>';
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
						if (!data) return false;
						if (data.success === false) {
							return false;
						}
						if (typeof (data) == "string") data = eval('(' + data + ')');
						return data;
					}
				}
			});
		},
		findAndUpdateItem: function (barcode, quantity) {
			var item = this.model.get('lineItems').find(function (x) {
				return x.get('barcode') == barcode;
			});

			if (item) {
				var q = item.get('quantity');
				item.set({
					'quantity': q + quantity
				});
				$('input[name=itemName]').val(item.get('name'))
				this.vent.trigger('updateOrder', this.model.get('orderid'))
				return true;
			}
			return false;
		},
		addLineItem: function () {
			if (!this.model) {
				this.newOrder(function () {
					$('#add-item').trigger('click');
				});
				return;
			}
			var $txtBarcode = $('input[name=barcode]');
			var barcode = $txtBarcode.val();
			var tmp = $('input[name=quantity]').val();
			var quantity = 1.0;
			if (tmp && tmp.length > 0) quantity = parseFloat(tmp);

			if (barcode && barcode.length > 0 && quantity > 0) {
				var found = this.findAndUpdateItem(barcode, quantity)
				if (!found) {
					var that = this

					remote.searchItem(barcode, function (data) {
						if (typeof (data) == "string") data = eval('(' + data + ')');
						if (data) {
							if (data.length > 1) {
								var compl = _.template($('#tpl-selectitem').html());
								var tr = compl({
									'items': data
								});
								$('#tblSelectItem tbody').html(tr);

								$('#tblSelectItem tbody td button').each(function () {
									$(this).click(function () {
										var id = parseInt($(this).data('id'));
										data[id].Quantity = quantity;
										that.addItemToUI(data[id], that);

										$('#tblSelectItem tbody').html('');
										$('#selectItemModal').modal('hide');
										$('input[name=itemName]').val(data[id].Name)
										$txtBarcode[0].select(0, barcode.length)
									});
								});

								// show pop to select the item
								$('#selectItemModal').modal('show');
							} else {
								data[0].Quantity = quantity;
								that.addItemToUI(data[0], that);
								$('input[name=itemName]').val(data[0].Name)
								$txtBarcode[0].select(0, $txtBarcode.val().length);
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
									d.ProductId = null
									that.addItemToUI(d, that)
								} else {
									showMsg('warn', '<strong>Oops!</strong> There are no items with barcode <span class="label label-info">' + barcode + '</span>.');
								}
							} else {
								showMsg('warn', '<strong>Oops!</strong> There are no items with barcode <span class="label label-info">' + barcode + '</span>.');
							}

							$txtBarcode[0].select(0, barcode.length);
						}
					});
				} else {
					$txtBarcode[0].select(0, $txtBarcode.val().length);
				}
			} else {
				showMsg('warn', '<strong>Enter a valid barcode!</strong>');
				$txtBarcode[0].select(0, $txtBarcode.val().length);
			}
		},
		addItemToUI: function (data, that) {
			var barcode = data.Barcode;
			var itemName = data.Name;
			var price = Math.round(data.SellPrice);
			var discount = data.Discount;
			var mrp = data.MRP;
			var quantity = data.Quantity;

			var item = new LineItem({
				id: uuid(),
				orderid: that.model.get('orderid'),
				productid: data.ProductId,
				name: itemName,
				barcode: barcode,
				mrp: mrp,
				quantity: quantity,
				price: price,
				discount: discount,
				subtotal: Math.round(price * quantity)
			});

			item.hasMultiple = data.hasMultiple
			that.model.get('lineItems').add(item)
			that.vent.trigger('updateOrder', that.model.get('orderid'))
		},
		newOrderClick: function (e) {
			this.newOrder(function () {
				var $txtBarcode = $('input[name=barcode]');
				$txtBarcode[0].select(0, $txtBarcode.val().length);
			});
		},
		newOrder: function (callback) {
			if (this.model) {
				var items = this.model.get('lineItems');
				items.resetRecords();
			}

			this.model = new Order;
			this.model.bind("change", this.render, this);
			this.model.get('lineItems').reset();
			this.model.get('payments').reset();

			var lstorders = this.lstOrders;
			var currentOrder = this.model;

			remote.newOrder(function (data) {
				if (data) {
					currentOrder.set({
						'id': data.Id,
						'orderid': data.Id,
						'customerid': data.CustomerId,
						'customername': data.CustomerName,
						'orderno': data.OrderNo,
						'orderdate': data.OrderDate,
						'paidamount': data.PaidAmount,
						'orderamount': data.OrderAmount,
						'isNew': true,
					});
					lstorders.add(currentOrder)
					hideMsg()
					if (callback) callback()
				}
			});
		},
		editOrder: function (orderid) {
			if (!orderid || (this.model && orderid == this.model.get('orderid'))) return

			found = this.lstOrders.find(function (x) {
				return x.get('orderid') == orderid;
			});

			if (found) {
				this.model = found
				this.model.bind("change", this.render, this);
				if (!found.get('isloaded') === true) {
					this.fetchAndEditOrder(orderid)
				} else {
					var that = this
					this.model.get('lineItems').refreshUI(function () {
						that.render()
						var $txtBarcode = $('input[name=barcode]');
						$txtBarcode[0].select(0, $txtBarcode.val().length);
					})
				}
			} else {
				showMsg('error', '<strong>Oops!</strong> Something went really wrong.')
			}
		},
		fetchAndEditOrder: function (orderid) {
			var currentOrder = this.model;
			var items = this.model.get('lineItems');

			items.refreshUI();
			$.post('/sales/getorder/' + orderid, null, function (data) {
				if (typeof (data) == "string") data = eval('(' + data + ')');
				if (data) {
					var o = data.order;
					var orderid = o.Id;
					var lineitems = data.lineitems;
					var payments = data.payments;

					currentOrder.set({
						'id': o.Id,
						'orderid': o.Id,
						'customerid': o.CustomerId,
						'customername': o.CustomerName,
						'orderno': o.OrderNo,
						'orderdate': o.OrderDate,
						'paidamount': o.PaidAmount,
						'orderamount': o.OrderAmount,
						'isloaded': true,
					});

					if (lineitems) {
						for (var i = 0; i < lineitems.length; i++) {
							var price = Math.round(lineitems[i].SellPrice);
							var quantity = lineitems[i].Quantity;
							var item = new LineItem({
								id: uuid(),
								productid: lineitems[i].ProductId,
								name: lineitems[i].Name,
								barcode: lineitems[i].Barcode,
								mrp: lineitems[i].MRP,
								quantity: quantity,
								price: price,
								discount: lineitems[i].Discount,
								subtotal: Math.round(price * quantity)
							});
							currentOrder.get('lineItems').add(item);
						}
					}

					if (payments) {
						for (var i = 0; i < payments.length; i++) {
							var no = i + 1;
							var item = new OrderPayment({
								slno: no,
								orderid: orderid,
								paidamount: payments[i].PaidAmount,
								paymenttype: payments[i].PaymentType,
								paymentdate: payments[i].PaymentDate,
							});
							currentOrder.get('payments').add(item);
						}
					}

					currentOrder.set({
						'ispaid': (payments && payments.length > 0),
						'paidamount': currentOrder.getPaidAmount(),
						'orderamount': currentOrder.getOrderAmount(),
					});

					var $txtBarcode = $('input[name=barcode]');
					$txtBarcode[0].select(0, $txtBarcode.val().length);
				}
			});
		},
		cancelOrder: function () {
			if (this.model) {
				this.model.get('lineItems').reset()
				this.model.get('payments').reset()
				this.vent.trigger('updateOrder', this.model.get('orderid'))
				this.render()
				var $txtBarcode = $('input[name=barcode]')
				$txtBarcode[0].select(0, $txtBarcode.val().length)
			}
		},
		checkOutOrder: function () {
			if (!this.model || this.model.get('lineItems').length < 1) {
				showMsg('warn', '<strong>Oops!</strong> Order contains no items. Cannot <span class="label label-info">checkout</span>.', false);
				return;
			}

			var orderamt = this.model.getOrderAmount();
			var paidamt = this.model.getPaidAmount();
			var balanceamt = paidamt > orderamt ? 0.0 : (orderamt - paidamt)
			this.model.set({
				'orderamount': orderamt,
				'balanceamount': balanceamt,
			});

			var cmpl = _.template($('#tpl-chkoutorder').html());
			var html = cmpl({
				'item': this.model
			});
			$('#checkoutOrderModel table tbody').html(html);

			$('#checkoutOrderModel').modal('show');

			$('input[name=customername]', $('#checkoutOrderModel')).typeahead({
				idField: 'id',
				idControl: $('input[name=customerid]', $('#checkoutOrderModel')),
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
						var fieldName = $('input[type=radio][name=searchfield]:checked').val();
						this.displayField = fieldName;
						return {
							search: query,
							field: fieldName || 'name'
						}
					},
					preProcess: function (data) {
						//showLoadingMask(false);
						if (!data || !data.mylist) return false;
						if (data.success === false) {
							return false;
						}
						if (typeof (data.mylist) == "string") data.mylist = eval('(' + data.mylist + ')');
						// We good!
						return data.mylist;
					}
				}
			});

			$('#btnPayOrder', $('#checkoutOrderModel'))[0].focus()
			$('#btnPayOrder', $('#checkoutOrderModel')).unbind('click', this.payOrder)
			$('#btnPayOrder', $('#checkoutOrderModel')).click(this.payOrder)
		},
		payOrder: function () {
			var customerid = $('input[name=customerid]', $('#checkoutOrderModel')).val();

			if (customerid) {
				var orderid = salesappview.model.get('orderid');
				var paidamount = parseFloat($('input[name=paidamount]', $('#checkoutOrderModel')).val());
				var customername = $('input[name=customername]', $('#checkoutOrderModel')).val();
				var paymenttype = $('select[name=paymenttype] option:selected', $('#checkoutOrderModel')).val();
				var orderamount = salesappview.model.getOrderAmount();
				var prevpaidamt = salesappview.model.getPaidAmount();

				if ((paymenttype == 'Cash' && (prevpaidamt + paidamount >= orderamount)) || (paymenttype == 'Credit' && paidamount < orderamount) || (paymenttype == 'Card' && paidamount > 0.0) || (paymenttype == 'Cheque' && paidamount > 0.0)) {
					salesappview.model.set({
						'paidamount': prevpaidamt + paidamount,
						'customerid': customerid,
						'customername': customername,
						'ispaid': true,
						'isloaded': true,
					});

					var payment = new OrderPayment({
						'orderid': orderid,
						'paidamount': paidamount,
						'paymenttype': paymenttype,
						'paymentdate': new Date().toUTCString(),
					});

					salesappview.model.get('payments').add(payment);
					salesappview.model.save();
					showMsg('success', '<strong>Hooray!</strong> Payment Successfull &amp; Order is saved.');
				} else if (paymenttype == 'Credit' && paidamount >= orderamount) {
					showMsg('warn', '<strong>Oops!</strong> Wrong Payment Type. Please choose <span class="label label-info">Cash</span> as payment type if the paid amount is greater than order amount.');
				} else {
					showMsg('warn', 'Paid amount should be greater than or equal to <strong>' + orderamount + '</strong>. Please choose <span class="label label-info">Credit</span> as payment type if the paid amount is lesser than order amount.');
				}
			} else {
				showMsg('error', '<strong>Oops!</strong> Please enter a valid customer to save this order.');
			}

			$(this).unbind('click', salesappview.payOrder);
			$('#checkoutOrderModel').modal('hide');
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
				showMsg('info', 'No active order! Cannot print!')
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


/*$('#tblTodayOrders tbody').on('dblclick', "tr", function (e) {
		$('#tblTodayOrders tbody').find('.active').removeClass('active')
		$(this).addClass('active')
		var orderid = $(this).data('orderid')
		//if (orderid) salesappview.editOrder(orderid)
		if(orderid) vent.trigger('editOrder',orderid)
		//e.preventDefault()
	});*/
	
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

	function hideMsg() {
		$('#statusMessage').fadeOut();
	}

	function showMsg(type, message, timeout) {
		var ediv = '<div class="alert ';
		if (type == "error") {
			ediv += 'alert-error';
		} else if (type == "info") {
			ediv += 'alert-info';
		} else if (type == "success") {
			ediv += 'alert-success';
		} else if (type == "warn") {
			ediv += 'alert-warning';
		} else {
			ediv += '';
		}
		ediv += ' fade in">';
		ediv += '<a class="close" data-dismiss="alert" href="#">&times;</a>';
		ediv += message;
		ediv += '</div>';
		$('#statusMessage').html(ediv);
		$('.alert', $('#statusMessage')).alert();

		if (timeout || timeout == undefined) {
			setTimeout(function () {
				$('.alert', $('#statusMessage')).alert('close');
			}, 10000);
		}
	}

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
			$tb = $('input[name="barcode"]')
			$tb[0].select(0, $tb.val().length)
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

	$(document).bind('keypress', listen);
})(jQuery);
