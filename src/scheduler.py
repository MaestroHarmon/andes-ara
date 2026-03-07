import heapq

class Request:
    def __init__(self, id, context_length, expected_ttft, expected_tds):
        self.id = id
        self.context_length = context_length
        self.expected_ttft = expected_ttft
        self.expected_tds = expected_tds
        self.tokens_generated = 0
        self.priority = 0  # Initialize priority
        self.start_time = None
        self.preemptions = 0

    def calculate_qoe_gain(self, batch_size):
        """
        Calculates the QoE gain of serving this request in a given batch.
        This is a simplified version based on the paper's description.
        """
        q_serve = self.calculate_qoe(self.tokens_generated + batch_size)
        q_wait = self.calculate_qoe(self.tokens_generated)

        return q_serve - q_wait

    def calculate_qoe(self, tokens_delivered):
        """
        Simplified QoE calculation.  Assumes linear delivery.
        """
        if tokens_delivered == 0:
            return 0
        time_to_tokens = self.expected_ttft + (tokens_delivered / self.expected_tds)
        # In a real implementation, this would compare against the *expected* timeline
        # and penalize deviations.  Here, we simply reward more tokens faster, up to a point.
        return min(1.0, tokens_delivered / (self.expected_tds * 10)) # Scale down to avoid QoE > 1

    def update_priority(self, batch_size, memory_constraint):
      """
      Updates the request's priority based on QoE gain and resource usage.
      """
      qoe_gain = self.calculate_qoe_gain(batch_size)
      #print(f"Request {self.id}: QoE Gain = {qoe_gain}, Context Length = {self.context_length}") #Debugging
      # Avoid division by zero if context_length is 0.
      self.priority = qoe_gain / (self.context_length if self.context_length > 0 else 1)

    def __lt__(self, other):
        # For the heapq, we want to retrieve the *highest* priority, so we use the negative.
        return self.priority > other.priority

class QoEAwareScheduler:
    def __init__(self, total_gpu_memory, preemption_cap=1):
        self.total_gpu_memory = total_gpu_memory
        self.available_gpu_memory = total_gpu_memory
        self.waiting_queue = []  # Priority queue (heap)
        self.running_requests = {} # Dictionary of running requests
        self.preemption_cap = preemption_cap

    def admit_request(self, request):
        """
        Admits a new request to the waiting queue.
        """
        heapq.heappush(self.waiting_queue, request)

    def schedule(self, batch_size):
        """
        Schedules requests based on QoE gain and resource usage, considering preemption.
        """
        # Update priorities of all waiting requests
        for request in self.waiting_queue:
            request.update_priority(batch_size, self.total_gpu_memory)

        # Sort waiting queue by priority (highest priority first)
        heapq.heapify(self.waiting_queue)

        selected_requests = []
        memory_used = 0

        #Greedy packing
        temp_queue = self.waiting_queue[:] #Copy queue
        heapq.heapify(temp_queue)
        while temp_queue and len(selected_requests) < batch_size:
            request = heapq.heappop(temp_queue)
            if request.context_length <= self.available_gpu_memory - memory_used:
                selected_requests.append(request)
                memory_used += request.context_length
            else:
                continue #Skip if no memory available

        #Preemption logic
        if memory_used > self.available_gpu_memory:
            #Sort running processes by lowest priority
            running_sorted = sorted(self.running_requests.values(), key=lambda x: x.priority)
            for req in running_sorted:
                if req.preemptions >= self.preemption_cap:
                    continue
                self.preempt(req)
                memory_used -= req.context_length
                if memory_used <= self.available_gpu_memory:
                    break

        #Allocate GPU resources
        for request in selected_requests:
            if request.start_time is None:
                request.start_time = 0 #current_time
            self.running_requests[request.id] = request
            self.available_gpu_memory -= request.context_length
            self.waiting_queue.remove(request) #Remove request from waiting queue
            heapq.heapify(self.waiting_queue)

        return selected_requests

    def preempt(self, request):
        """
        Preempts a running request.  In a real system, this would involve
        moving the KV cache to CPU memory.
        """
        print(f"Preempting request {request.id}")
        request.preemptions += 1
        self.available_gpu_memory += request.context_length
        del self.running_requests[request.id]
        heapq.heappush(self.waiting_queue, request) # Add back to waiting queue

    def complete_request(self, request_id, batch_size):
        """
        Completes a request and releases its resources.
        """
        if request_id in self.running_requests:
            request = self.running_requests[request_id]
            self.available_gpu_memory += request.context_length
            del self.running_requests[request_id]
            return request.calculate_qoe(batch_size)
        else:
            return 0