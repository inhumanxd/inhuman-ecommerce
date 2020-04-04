from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, View
from .models import Item, OrderItem, Order
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.contrib import messages
from django.core.mail import send_mail


class HomeView(ListView):
    model = Item
    context_object_name = 'products'
    template_name = 'home.html'

    
def OrderConfirmation(request):
    if request.method == "POST":
        receiverID = request.POST['emailID']
        items = Item.objects.all()
        order_qs = Order.objects.filter(user=request.user, ordered=False)
        count = 0
        ORDER = {}

        if order_qs.exists():
            for order in order_qs:
                
                order_items = order.items.all()
                for order_item in order_items:
                    item = Item.objects.get(title=order_item.item.title)
                    available_quantity = item.quantity
                    if item.quantity>order_item.quantity:
                        count += 1
                        
                if(count == order_items.count()):
                    i = 1
                    for order_item in order_items:
                        
                        print(i)
                        ORDER[i] = {}
                        item = Item.objects.get(title=order_item.item.title)
                        available_quantity = item.quantity
                        item.quantity = item.quantity - order_item.quantity
                        order_item.ordered = True
                        item.save()
                        order_item.save()
                        
                        ORDER[i]['title'] = order_item.item.title
                        ORDER[i]['quantity'] = order_item.quantity
                        ORDER[i]['price'] = order_item.item.price
                        i+=1
                    status = True    
                else:
                    status = False
                ORDER['total'] = order.get_total()    
                if status == True:
                    order.ordered=True
                    message = f"Your order was successful.\nOrder Details:{ORDER}"
                    messages.info(request, "Your order was successful. Check email for details.")
                    order.save()

                else: 
                    messages.info(request, "Your order could not be processed.")
                    message = "Your order could not be processed because item's stock is not enough."    
                
                send_mail('Order Confirmation', 
                    message, 
                    'indiansoldier2601@gmail.com', 
                    [receiverID]
                                                )
            return redirect('/')
        else:                                    
            messages.info(request, "Your order could not be processed.")
        return redirect('/')
    messages.info(request, "Your order could not be processed.")
    return redirect('/')    

def Search(request):
    if request.method == "POST":
        search_input = request.POST['search_input']
        products = Item.objects.filter(title__icontains=search_input)
        if products:
            context = {
                'products': products
            }
            return render(request, 'search.html', context) 
        else:
            messages.info(request, "No Items found.")
            return render(request, 'search.html')            
    return render(request, 'search.html')        


class CartView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):

        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'cart.html', context)

        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order.")
            return redirect('/')    
           
@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(item=item, user=request.user, ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This product's quantity updated.")
        else:
            messages.info(request, "This product's added to your cart.")
            order.items.add(order_item)    
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date= ordered_date)  
        messages.info(request, "This product's added to your cart.")
        order.items.add(order_item)      
    return redirect("home")

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            order_item.quantity = 0
            order.items.remove(order_item)   
            messages.info(request, "This product's removed from your cart.")
            return redirect("cart")
        else:
            messages.info(request, "This product is not in your cart.")
            return redirect("cart")    
    else:
        messages.info(request, "You do not have an active order.")
        return redirect("cart")

@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            if(order_item.quantity == 1):
                order_item.quantity = 0
                order.items.remove(order_item)  
                return redirect("cart") 
            order_item.quantity -= 1
            order_item.save()   
            messages.info(request, "This product's quantity was updated.")
            return redirect("cart")
        else:
            messages.info(request, "This product is not in your cart.")
            return redirect("cart")    
    else:
        messages.info(request, "You do not have an active order.")
        return redirect("cart") 


@login_required
def add_single_item_in_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            order_item.quantity += 1
            order_item.save()   
            messages.info(request, "This product's quantity was updated.")
            return redirect("cart")
        else:
            messages.info(request, "This product is not in your cart.")
            return redirect("cart")    
    else:
        messages.info(request, "You do not have an active order.")
        return redirect("cart")         